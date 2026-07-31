"""On-demand research-only assessment endpoints (Phase 6, ADR-0007).

Protected by operator session auth. No recommendations, actionable promotion, or order
placement. Assessments are fail-closed: gate failures return HTTP 422 and persist nothing.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from aegis.api.dependencies import (
    build_outcome_label_service,
    build_research_calibration_service,
    enrich_assessment_with_calibration,
    get_outcome_label_service,
    get_research_assessment_service,
    get_research_calibration_repository,
    get_research_calibration_service,
    require_operator,
)
from aegis.api.schemas.research import (
    AssessmentBackfillItem,
    AssessmentBackfillResponse,
    ResearchAssessmentResponse,
)
from aegis.api.schemas.research_calibration_readiness import CalibrationReadinessResponse
from aegis.api.schemas.research_evidence_summary import ResearchEvidenceSummaryResponse
from aegis.api.schemas.research_outcome_labels import (
    OutcomeLabelBackfillItem,
    OutcomeLabelBackfillResponse,
    OutcomeLabelResponse,
)
from aegis.api.schemas.research_probability_calibration import ProbabilityCalibrationResponse
from aegis.domain.research_assessment import (
    ASSESSMENT_FILTER_SCAN_LIMIT,
    ResearchAssessmentService,
    ResearchAssessmentUnavailableError,
    component_source_of,
    count_mixed_unlabeled_assessments,
    filter_assessments_by_component_source,
    is_mixed_component_source,
)
from aegis.domain.research_outcome_labels import (
    OutcomeLabelService,
    OutcomeLabelUnavailableError,
    resolve_label_bar_source,
)
from aegis.domain.research_probability_calibration import (
    CalibrationUnavailableError,
    ResearchProbabilityCalibrationService,
)
from aegis.domain.scheduled_calibration import try_calibrate_assessment_after_create
from aegis.domain.scheduled_outcome_labels import (
    run_outcome_labels_after_assessments,
    try_label_assessment_after_create,
)
from aegis.persistence.repositories.market_data import MarketDailyBarRepository
from aegis.persistence.repositories.research_assessment import ResearchAssessmentRepository
from aegis.persistence.repositories.research_outcome_labels import ResearchOutcomeLabelRepository
from aegis.persistence.repositories.research_probability_calibration import (
    ResearchProbabilityCalibrationRepository,
)

router = APIRouter(
    prefix="/research",
    tags=["research"],
    dependencies=[Depends(require_operator)],
)


@router.post(
    "/{symbol}/assessments",
    response_model=ResearchAssessmentResponse,
    status_code=status.HTTP_200_OK,
)
async def create_research_assessment(
    request: Request,
    symbol: str,
    service: ResearchAssessmentService = Depends(get_research_assessment_service),
) -> ResearchAssessmentResponse:
    """Compute and append a research-only assessment for ``symbol`` from stored bars."""

    try:
        snapshot = await service.assess(symbol)
    except ResearchAssessmentUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"reason": exc.reason.value, "message": exc.detail},
        ) from exc
    settings = request.app.state.settings
    if settings.research_outcome_label_after_assessment_enabled or (
        settings.research_calibration_after_label_enabled
    ):
        async with request.app.state.db_session_factory() as session:
            market_data_repository = MarketDailyBarRepository(session)
            assessment_repository = ResearchAssessmentRepository(session)
            calibration_repository = ResearchProbabilityCalibrationRepository(session)
            if settings.research_outcome_label_after_assessment_enabled:
                outcome_label_service = build_outcome_label_service(
                    market_data_repository,
                    assessment_repository,
                    ResearchOutcomeLabelRepository(session),
                    settings,
                )
                await try_label_assessment_after_create(snapshot, outcome_label_service)
            if settings.research_calibration_after_label_enabled:
                calibration_service = build_research_calibration_service(
                    assessment_repository,
                    calibration_repository,
                    settings,
                )
                await try_calibrate_assessment_after_create(snapshot, calibration_service)
            snapshot = await enrich_assessment_with_calibration(
                snapshot,
                calibration_repository,
            )
    return ResearchAssessmentResponse.model_validate(snapshot)


@router.post(
    "/{symbol}/assessments/backfill",
    response_model=AssessmentBackfillResponse,
    status_code=status.HTTP_200_OK,
)
async def backfill_research_assessments(
    symbol: str,
    limit: int = Query(default=20, ge=1, le=100),
    service: ResearchAssessmentService = Depends(get_research_assessment_service),
) -> AssessmentBackfillResponse:
    """Create point-in-time assessments for recent primary bar dates (ADR-0046).

    Always returns 200 with a per-date summary. Does not invent probability_confidence or
    run labeling/calibration.
    """

    summary = await service.backfill_assessments(symbol, limit)
    return AssessmentBackfillResponse(
        symbol=symbol.upper(),
        candidate_count=summary.candidate_count,
        persisted_count=summary.persisted_count,
        skipped_count=summary.skipped_count,
        outcomes=[
            AssessmentBackfillItem(
                symbol=outcome.symbol,
                as_of_trading_date=outcome.as_of_trading_date,
                persisted=outcome.persisted,
                assessment_snapshot_id=outcome.assessment_snapshot_id,
                reason=outcome.reason,
                detail=outcome.detail,
            )
            for outcome in summary.outcomes
        ],
    )


@router.post(
    "/{symbol}/outcome-labels/backfill",
    response_model=OutcomeLabelBackfillResponse,
    status_code=status.HTTP_200_OK,
)
async def backfill_outcome_labels(
    symbol: str,
    limit: int = Query(default=100, ge=1, le=252),
    assessment_service: ResearchAssessmentService = Depends(get_research_assessment_service),
    label_service: OutcomeLabelService = Depends(get_outcome_label_service),
) -> OutcomeLabelBackfillResponse:
    """Re-attempt Phase 13 labeling over unlabeled label-ready assessments (ADR-0050/0058).

    Always returns 200 with a per-assessment summary. Individual fail-closed skips do not
    abort the batch. Does not invent probability_confidence or enable auto-calibration.
    Default ``limit`` is 100 (ADR-0058); scan depth is ``BACKFILL_SCAN_LIMIT``.
    """

    from aegis.domain.research_outcome_label_backfill import BACKFILL_SCAN_LIMIT

    snapshots = await assessment_service.list_assessments(symbol, BACKFILL_SCAN_LIMIT)
    pairs = await label_service.select_backfill_candidates(symbol, snapshots, limit)
    summary = await run_outcome_labels_after_assessments(pairs, label_service)
    return OutcomeLabelBackfillResponse(
        symbol=symbol.upper(),
        assessment_count=len(pairs),
        persisted_count=summary.persisted_count,
        skipped_count=summary.skipped_count,
        outcomes=[
            OutcomeLabelBackfillItem(
                symbol=outcome.symbol,
                assessment_snapshot_id=outcome.assessment_snapshot_id,
                persisted=outcome.persisted,
                reason=outcome.reason,
                detail=outcome.detail,
            )
            for outcome in summary.outcomes
        ],
    )


@router.post(
    "/{symbol}/assessments/{assessment_id}/outcome-labels",
    response_model=OutcomeLabelResponse,
    status_code=status.HTTP_200_OK,
)
async def create_outcome_labels(
    symbol: str,
    assessment_id: int,
    service: OutcomeLabelService = Depends(get_outcome_label_service),
) -> OutcomeLabelResponse:
    """Compute and append forward-return outcome labels for an assessment snapshot."""

    try:
        label = await service.label_assessment(symbol, assessment_id)
    except OutcomeLabelUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"reason": exc.reason.value, "message": exc.detail},
        ) from exc
    return OutcomeLabelResponse.model_validate(label)


@router.get(
    "/{symbol}/assessments/{assessment_id}/outcome-labels",
    response_model=list[OutcomeLabelResponse],
)
async def list_outcome_labels(
    symbol: str,
    assessment_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    service: OutcomeLabelService = Depends(get_outcome_label_service),
) -> list[OutcomeLabelResponse]:
    """Return up to ``limit`` outcome labels for ``assessment_id``, newest first."""

    rows = await service.list_labels_for_assessment(symbol, assessment_id, limit)
    return [OutcomeLabelResponse.model_validate(item) for item in rows]


@router.get("/{symbol}/assessments/{assessment_id}/outcome-labels/export")
async def export_outcome_labels(
    symbol: str,
    assessment_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    service: OutcomeLabelService = Depends(get_outcome_label_service),
) -> JSONResponse:
    """Download outcome-label history as a JSON attachment (ADR-0035)."""

    rows = await service.list_labels_for_assessment(symbol, assessment_id, limit)
    payload = [
        OutcomeLabelResponse.model_validate(item).model_dump(mode="json") for item in rows
    ]
    filename = (
        f"aegis-{symbol.upper()}-assessment-{assessment_id}-outcome-labels.json"
    )
    return JSONResponse(
        content=payload,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/{symbol}/assessments/{assessment_id}/outcome-labels/latest",
    response_model=OutcomeLabelResponse,
)
async def get_latest_outcome_labels(
    symbol: str,
    assessment_id: int,
    service: OutcomeLabelService = Depends(get_outcome_label_service),
) -> OutcomeLabelResponse:
    """Return the latest outcome labels for ``assessment_id``, or 404."""

    label = await service.latest_label_for_assessment(assessment_id)
    if label is None or label.symbol.upper() != symbol.upper():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no outcome labels for assessment {assessment_id}",
        )
    return OutcomeLabelResponse.model_validate(label)


@router.post(
    "/{symbol}/assessments/{assessment_id}/calibrations",
    response_model=ProbabilityCalibrationResponse,
    status_code=status.HTTP_200_OK,
)
async def create_probability_calibration(
    symbol: str,
    assessment_id: int,
    horizon: str = Query(
        default="forward_return_5",
        description="Outcome label horizon key (forward_return_5 or forward_return_20).",
    ),
    service: ResearchProbabilityCalibrationService = Depends(get_research_calibration_service),
) -> ProbabilityCalibrationResponse:
    """Compute and append research_calibration_v1 for ``assessment_id`` (fail-closed)."""

    try:
        from aegis.domain.research_probability_calibration import normalize_outcome_horizon_key

        horizon_key = normalize_outcome_horizon_key(horizon)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"reason": "unsupported_horizon", "message": str(exc)},
        ) from exc

    try:
        calibration = await service.calibrate_assessment(
            symbol, assessment_id, outcome_horizon_key=horizon_key
        )
    except CalibrationUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"reason": exc.reason.value, "message": exc.detail},
        ) from exc
    return ProbabilityCalibrationResponse.model_validate(calibration)


@router.get(
    "/{symbol}/assessments/{assessment_id}/calibrations",
    response_model=list[ProbabilityCalibrationResponse],
)
async def list_probability_calibrations(
    symbol: str,
    assessment_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    service: ResearchProbabilityCalibrationService = Depends(get_research_calibration_service),
) -> list[ProbabilityCalibrationResponse]:
    """Return up to ``limit`` calibrations for ``assessment_id``, newest first."""

    rows = await service.list_calibrations_for_assessment(symbol, assessment_id, limit)
    return [ProbabilityCalibrationResponse.model_validate(item) for item in rows]


@router.get("/{symbol}/assessments/{assessment_id}/calibrations/export")
async def export_probability_calibrations(
    symbol: str,
    assessment_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    service: ResearchProbabilityCalibrationService = Depends(get_research_calibration_service),
) -> JSONResponse:
    """Download calibration history as a JSON attachment (ADR-0037)."""

    rows = await service.list_calibrations_for_assessment(symbol, assessment_id, limit)
    payload = [
        ProbabilityCalibrationResponse.model_validate(item).model_dump(mode="json")
        for item in rows
    ]
    filename = (
        f"aegis-{symbol.upper()}-assessment-{assessment_id}-calibrations.json"
    )
    return JSONResponse(
        content=payload,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/{symbol}/assessments/{assessment_id}/calibrations/latest",
    response_model=ProbabilityCalibrationResponse,
)
async def get_latest_probability_calibration(
    symbol: str,
    assessment_id: int,
    service: ResearchProbabilityCalibrationService = Depends(get_research_calibration_service),
) -> ProbabilityCalibrationResponse:
    """Return the latest calibration for ``assessment_id``, or 404."""

    calibration = await service.latest_calibration_for_assessment(assessment_id)
    if calibration is None or calibration.symbol.upper() != symbol.upper():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no probability calibration for assessment {assessment_id}",
        )
    return ProbabilityCalibrationResponse.model_validate(calibration)


async def _build_research_evidence_summary(
    symbol: str,
    *,
    assessment_service: ResearchAssessmentService,
    outcome_label_service: OutcomeLabelService,
    calibration_service: ResearchProbabilityCalibrationService,
    calibration_repository: ResearchProbabilityCalibrationRepository,
) -> ResearchEvidenceSummaryResponse:
    """Compose the Phase 22 research-only evidence aggregate (null/zero missing fields)."""

    snapshots = await assessment_service.list_assessments(symbol, 100)
    assessment_count = len(snapshots)
    snapshot = snapshots[0] if snapshots else None
    readiness = await calibration_service.evaluate_readiness(symbol, snapshot)

    latest_assessment = None
    latest_outcome_label = None
    latest_calibration = None
    outcome_label_count = 0
    calibration_count = 0
    latest_component_source = None
    latest_resolved_label_bar_source = None
    mixed_component_source_assessment_count = sum(
        1 for row in snapshots if is_mixed_component_source(row)
    )
    scanned_ids = [row.id for row in snapshots if row.id is not None]
    labeled_ids = (
        await outcome_label_service.assessment_ids_with_labels(symbol, scanned_ids)
        if scanned_ids
        else set()
    )
    labeled_assessment_count = sum(1 for row_id in scanned_ids if row_id in labeled_ids)
    unlabeled_assessment_count = max(0, assessment_count - labeled_assessment_count)
    mixed_unlabeled_assessment_count = count_mixed_unlabeled_assessments(
        snapshots, labeled_ids
    )
    if mixed_unlabeled_assessment_count > mixed_component_source_assessment_count:
        mixed_unlabeled_assessment_count = mixed_component_source_assessment_count
    mixed_labeled_assessment_count = (
        mixed_component_source_assessment_count - mixed_unlabeled_assessment_count
    )
    latest_mixed_label_bar_source = None
    for row in snapshots:
        if row.id is None or not is_mixed_component_source(row):
            continue
        if row.id not in labeled_ids:
            continue
        mixed_labels = await outcome_label_service.list_labels_for_assessment(
            symbol, row.id, 1
        )
        if mixed_labels:
            latest_mixed_label_bar_source = mixed_labels[0].bar_source
            break

    most_recent_labeled_assessment_id: int | None = None
    most_recent_labeled_outcome_label = None
    for row in snapshots:
        if row.id is None or row.id not in labeled_ids:
            continue
        scan_labels = await outcome_label_service.list_labels_for_assessment(
            symbol, row.id, 1
        )
        if scan_labels:
            most_recent_labeled_assessment_id = row.id
            most_recent_labeled_outcome_label = OutcomeLabelResponse.model_validate(
                scan_labels[0]
            )
            break

    if snapshot is not None and snapshot.id is not None:
        enriched = await enrich_assessment_with_calibration(snapshot, calibration_repository)
        latest_assessment = ResearchAssessmentResponse.model_validate(enriched)
        latest_component_source = component_source_of(snapshot)
        latest_resolved_label_bar_source = resolve_label_bar_source(snapshot)
        labels = await outcome_label_service.list_labels_for_assessment(symbol, snapshot.id, 100)
        outcome_label_count = len(labels)
        if labels:
            latest_outcome_label = OutcomeLabelResponse.model_validate(labels[0])
            latest_resolved_label_bar_source = labels[0].bar_source
        calibrations = await calibration_service.list_calibrations_for_assessment(
            symbol, snapshot.id, 100
        )
        calibration_count = len(calibrations)
        if calibrations:
            latest_calibration = ProbabilityCalibrationResponse.model_validate(calibrations[0])

    latest_coverage_confidence = (
        latest_assessment.coverage_confidence if latest_assessment is not None else None
    )
    latest_research_index: float | None = None
    if latest_assessment is not None:
        raw_index = latest_assessment.components.get("research_index")
        if isinstance(raw_index, bool):
            latest_research_index = None
        elif isinstance(raw_index, (int, float)):
            latest_research_index = float(raw_index)
    latest_as_of_trading_date = (
        latest_assessment.as_of_trading_date if latest_assessment is not None else None
    )
    latest_bar_count = latest_assessment.bar_count if latest_assessment is not None else None
    latest_input_source = (
        latest_assessment.input_source if latest_assessment is not None else None
    )
    latest_method_id = latest_assessment.method_id if latest_assessment is not None else None
    latest_method_version = (
        latest_assessment.method_version if latest_assessment is not None else None
    )
    latest_lookback_end_date = (
        latest_assessment.lookback_end_date if latest_assessment is not None else None
    )

    return ResearchEvidenceSummaryResponse(
        symbol=symbol.upper(),
        state="research_only",
        latest_assessment=latest_assessment,
        calibration_readiness=CalibrationReadinessResponse.model_validate(readiness),
        latest_outcome_label=latest_outcome_label,
        latest_calibration=latest_calibration,
        assessment_count=assessment_count,
        labeled_assessment_count=labeled_assessment_count,
        unlabeled_assessment_count=unlabeled_assessment_count,
        outcome_label_count=outcome_label_count,
        calibration_count=calibration_count,
        latest_component_source=latest_component_source,
        latest_resolved_label_bar_source=latest_resolved_label_bar_source,
        mixed_component_source_assessment_count=mixed_component_source_assessment_count,
        mixed_unlabeled_assessment_count=mixed_unlabeled_assessment_count,
        mixed_labeled_assessment_count=mixed_labeled_assessment_count,
        latest_mixed_label_bar_source=latest_mixed_label_bar_source,
        most_recent_labeled_assessment_id=most_recent_labeled_assessment_id,
        most_recent_labeled_outcome_label=most_recent_labeled_outcome_label,
        latest_coverage_confidence=latest_coverage_confidence,
        latest_research_index=latest_research_index,
        latest_as_of_trading_date=latest_as_of_trading_date,
        latest_bar_count=latest_bar_count,
        latest_input_source=latest_input_source,
        latest_method_id=latest_method_id,
        latest_method_version=latest_method_version,
        latest_lookback_end_date=latest_lookback_end_date,
        detail=(
            "Research-only evidence summary — not advice; missing fields are null or zero, "
            "never invented."
        ),
    )


@router.get(
    "/{symbol}/evidence-summary",
    response_model=ResearchEvidenceSummaryResponse,
)
async def get_research_evidence_summary(
    symbol: str,
    assessment_service: ResearchAssessmentService = Depends(get_research_assessment_service),
    outcome_label_service: OutcomeLabelService = Depends(get_outcome_label_service),
    calibration_service: ResearchProbabilityCalibrationService = Depends(
        get_research_calibration_service
    ),
    calibration_repository: ResearchProbabilityCalibrationRepository = Depends(
        get_research_calibration_repository
    ),
) -> ResearchEvidenceSummaryResponse:
    """Return a read-only research evidence aggregate for ``symbol`` (ADR-0023)."""

    return await _build_research_evidence_summary(
        symbol,
        assessment_service=assessment_service,
        outcome_label_service=outcome_label_service,
        calibration_service=calibration_service,
        calibration_repository=calibration_repository,
    )


@router.get("/{symbol}/evidence-summary/export")
async def export_research_evidence_summary(
    symbol: str,
    assessment_service: ResearchAssessmentService = Depends(get_research_assessment_service),
    outcome_label_service: OutcomeLabelService = Depends(get_outcome_label_service),
    calibration_service: ResearchProbabilityCalibrationService = Depends(
        get_research_calibration_service
    ),
    calibration_repository: ResearchProbabilityCalibrationRepository = Depends(
        get_research_calibration_repository
    ),
) -> JSONResponse:
    """Download the research evidence aggregate as a JSON attachment (ADR-0025)."""

    summary = await _build_research_evidence_summary(
        symbol,
        assessment_service=assessment_service,
        outcome_label_service=outcome_label_service,
        calibration_service=calibration_service,
        calibration_repository=calibration_repository,
    )
    filename = f"aegis-{summary.symbol}-evidence-summary.json"
    return JSONResponse(
        content=summary.model_dump(mode="json"),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/{symbol}/calibration-readiness",
    response_model=CalibrationReadinessResponse,
)
async def get_calibration_readiness(
    symbol: str,
    assessment_service: ResearchAssessmentService = Depends(get_research_assessment_service),
    calibration_service: ResearchProbabilityCalibrationService = Depends(
        get_research_calibration_service
    ),
) -> CalibrationReadinessResponse:
    """Return corpus-gate readiness for ``symbol`` without persisting calibration rows."""

    snapshot = await assessment_service.latest_assessment(symbol)
    readiness = await calibration_service.evaluate_readiness(symbol, snapshot)
    return CalibrationReadinessResponse.model_validate(readiness)


@router.get("/{symbol}/calibration-readiness/export")
async def export_calibration_readiness(
    symbol: str,
    assessment_service: ResearchAssessmentService = Depends(get_research_assessment_service),
    calibration_service: ResearchProbabilityCalibrationService = Depends(
        get_research_calibration_service
    ),
) -> JSONResponse:
    """Download calibration readiness diagnostics as a JSON attachment (ADR-0033)."""

    snapshot = await assessment_service.latest_assessment(symbol)
    readiness = await calibration_service.evaluate_readiness(symbol, snapshot)
    payload = CalibrationReadinessResponse.model_validate(readiness)
    filename = f"aegis-{payload.symbol.upper()}-calibration-readiness.json"
    return JSONResponse(
        content=payload.model_dump(mode="json"),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{symbol}/assessments", response_model=list[ResearchAssessmentResponse])
async def list_research_assessments(
    symbol: str,
    limit: int = Query(default=20, ge=1, le=100),
    component_source: str | None = Query(
        default=None,
        description=(
            "Optional filter: exact match on assessment component source "
            "(e.g. mixed, alpha_vantage, polygon). Omit for unfiltered."
        ),
    ),
    service: ResearchAssessmentService = Depends(get_research_assessment_service),
    calibration_repository: ResearchProbabilityCalibrationRepository = Depends(
        get_research_calibration_repository
    ),
) -> list[ResearchAssessmentResponse]:
    """Return up to ``limit`` research assessments for ``symbol``, newest first."""

    snapshots = await _list_assessments_filtered(
        service, symbol, limit=limit, component_source=component_source
    )
    enriched = [
        await enrich_assessment_with_calibration(snapshot, calibration_repository)
        for snapshot in snapshots
    ]
    return [ResearchAssessmentResponse.model_validate(item) for item in enriched]


@router.get("/{symbol}/assessments/export")
async def export_research_assessments(
    symbol: str,
    limit: int = Query(default=20, ge=1, le=100),
    component_source: str | None = Query(
        default=None,
        description=(
            "Optional filter: exact match on assessment component source "
            "(e.g. mixed, alpha_vantage, polygon). Omit for unfiltered."
        ),
    ),
    service: ResearchAssessmentService = Depends(get_research_assessment_service),
    calibration_repository: ResearchProbabilityCalibrationRepository = Depends(
        get_research_calibration_repository
    ),
) -> JSONResponse:
    """Download assessment history as a JSON attachment (ADR-0039 / ADR-0062)."""

    snapshots = await _list_assessments_filtered(
        service, symbol, limit=limit, component_source=component_source
    )
    enriched = [
        await enrich_assessment_with_calibration(snapshot, calibration_repository)
        for snapshot in snapshots
    ]
    payload = [
        ResearchAssessmentResponse.model_validate(item).model_dump(mode="json")
        for item in enriched
    ]
    filename = f"aegis-{symbol.upper()}-assessments.json"
    return JSONResponse(
        content=payload,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


async def _list_assessments_filtered(
    service: ResearchAssessmentService,
    symbol: str,
    *,
    limit: int,
    component_source: str | None,
) -> list:
    """Load assessments; when filtering, scan then filter (ADR-0062)."""

    needle = component_source.strip() if isinstance(component_source, str) else ""
    if not needle:
        return await service.list_assessments(symbol, limit)
    scanned = await service.list_assessments(symbol, ASSESSMENT_FILTER_SCAN_LIMIT)
    return filter_assessments_by_component_source(
        scanned, needle, limit=limit
    )


@router.get(
    "/{symbol}/assessments/latest",
    response_model=ResearchAssessmentResponse,
)
async def get_latest_research_assessment(
    symbol: str,
    service: ResearchAssessmentService = Depends(get_research_assessment_service),
    calibration_repository: ResearchProbabilityCalibrationRepository = Depends(
        get_research_calibration_repository
    ),
) -> ResearchAssessmentResponse:
    """Return the latest research assessment for ``symbol``, or 404."""

    snapshot = await service.latest_assessment(symbol)
    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no research assessment for symbol {symbol!r}",
        )
    snapshot = await enrich_assessment_with_calibration(snapshot, calibration_repository)
    return ResearchAssessmentResponse.model_validate(snapshot)
