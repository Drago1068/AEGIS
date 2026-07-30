"""Response schema for symbol research evidence summary (Phase 22, ADR-0023)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from aegis.api.schemas.research import ResearchAssessmentResponse
from aegis.api.schemas.research_calibration_readiness import CalibrationReadinessResponse
from aegis.api.schemas.research_outcome_labels import OutcomeLabelResponse
from aegis.api.schemas.research_probability_calibration import ProbabilityCalibrationResponse


class ResearchEvidenceSummaryResponse(BaseModel):
    """Read-only research evidence aggregate. Never invents confidence or labels."""

    model_config = ConfigDict(from_attributes=True)

    symbol: str
    state: str = Field(description="Always research_only.")
    latest_assessment: ResearchAssessmentResponse | None = None
    calibration_readiness: CalibrationReadinessResponse
    latest_outcome_label: OutcomeLabelResponse | None = None
    latest_calibration: ProbabilityCalibrationResponse | None = None
    assessment_count: int = Field(ge=0)
    outcome_label_count: int = Field(ge=0)
    calibration_count: int = Field(ge=0)
    detail: str
