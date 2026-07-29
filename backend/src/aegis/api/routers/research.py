"""On-demand research-only assessment endpoints (Phase 6, ADR-0007).

Protected by operator session auth. No recommendations, actionable promotion, or order
placement. Assessments are fail-closed: gate failures return HTTP 422 and persist nothing.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from aegis.api.dependencies import (
    get_outcome_label_service,
    get_research_assessment_service,
    require_operator,
)
from aegis.api.schemas.research import ResearchAssessmentResponse
from aegis.api.schemas.research_outcome_labels import OutcomeLabelResponse
from aegis.domain.research_assessment import (
    ResearchAssessmentService,
    ResearchAssessmentUnavailableError,
)
from aegis.domain.research_outcome_labels import (
    OutcomeLabelService,
    OutcomeLabelUnavailableError,
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


@router.get("/{symbol}/assessments", response_model=list[ResearchAssessmentResponse])
async def list_research_assessments(
    symbol: str,
    limit: int = Query(default=20, ge=1, le=100),
    service: ResearchAssessmentService = Depends(get_research_assessment_service),
) -> list[ResearchAssessmentResponse]:
    """Return up to ``limit`` research assessments for ``symbol``, newest first."""

    snapshots = await service.list_assessments(symbol, limit)
    return [ResearchAssessmentResponse.model_validate(item) for item in snapshots]


@router.get(
    "/{symbol}/assessments/latest",
    response_model=ResearchAssessmentResponse,
)
async def get_latest_research_assessment(
    symbol: str,
    service: ResearchAssessmentService = Depends(get_research_assessment_service),
) -> ResearchAssessmentResponse:
    """Return the latest research assessment for ``symbol``, or 404."""

    snapshot = await service.latest_assessment(symbol)
    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no research assessment for symbol {symbol!r}",
        )
    return ResearchAssessmentResponse.model_validate(snapshot)
