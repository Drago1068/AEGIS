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
from aegis.api.schemas.research import ResearchAssessmentResponse
from aegis.api.schemas.research_calibration_readiness import CalibrationReadinessResponse
from aegis.api.schemas.research_evidence_summary import ResearchEvidenceSummaryResponse
from aegis.api.schemas.research_outcome_labels import OutcomeLabelResponse
from aegis.api.schemas.research_probability_calibration import ProbabilityCalibrationResponse
from aegis.domain.research_assessment import (
    ResearchAssessmentService,
    ResearchAssessmentUnavailableError,
)
from aegis.domain.research_outcome_labels import (
    OutcomeLabelService,
    OutcomeLabelUnavailableError,
)
from aegis.domain.research_probability_calibration import (
    CalibrationUnavailableError,
    ResearchProbabilityCalibrationService,
)
from aegis.domain.scheduled_calibration import try_calibrate_assessment_after_create
from aegis.domain.scheduled_outcome_labels import try_label_assessment_after_create
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
    service: ResearchProbabilityCalibrationService = Depends(get_research_calibration_service),
) -> ProbabilityCalibrationResponse:
    """Compute and append research_calibration_v1 for ``assessment_id`` (fail-closed)."""

    try:
        calibration = await service.calibrate_assessment(symbol, assessment_id)
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

    if snapshot is not None and snapshot.id is not None:
        enriched = await enrich_assessment_with_calibration(snapshot, calibration_repository)
        latest_assessment = ResearchAssessmentResponse.model_validate(enriched)
        labels = await outcome_label_service.list_labels_for_assessment(symbol, snapshot.id, 100)
        outcome_label_count = len(labels)
        if labels:
            latest_outcome_label = OutcomeLabelResponse.model_validate(labels[0])
        calibrations = await calibration_service.list_calibrations_for_assessment(
            symbol, snapshot.id, 100
        )
        calibration_count = len(calibrations)
        if calibrations:
            latest_calibration = ProbabilityCalibrationResponse.model_validate(calibrations[0])

    return ResearchEvidenceSummaryResponse(
        symbol=symbol.upper(),
        state="research_only",
        latest_assessment=latest_assessment,
        calibration_readiness=CalibrationReadinessResponse.model_validate(readiness),
        latest_outcome_label=latest_outcome_label,
        latest_calibration=latest_calibration,
        assessment_count=assessment_count,
        outcome_label_count=outcome_label_count,
        calibration_count=calibration_count,
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
    service: ResearchAssessmentService = Depends(get_research_assessment_service),
    calibration_repository: ResearchProbabilityCalibrationRepository = Depends(
        get_research_calibration_repository
    ),
) -> list[ResearchAssessmentResponse]:
    """Return up to ``limit`` research assessments for ``symbol``, newest first."""

    snapshots = await service.list_assessments(symbol, limit)
    enriched = [
        await enrich_assessment_with_calibration(snapshot, calibration_repository)
        for snapshot in snapshots
    ]
    return [ResearchAssessmentResponse.model_validate(item) for item in enriched]


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
