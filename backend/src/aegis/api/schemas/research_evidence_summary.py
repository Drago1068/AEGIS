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
    labeled_assessment_count: int = Field(
        default=0,
        ge=0,
        description=(
            "Count of scanned assessments (≤100 newest) that have a default-method "
            "outcome label. Never invented."
        ),
    )
    unlabeled_assessment_count: int = Field(
        default=0,
        ge=0,
        description=(
            "Count of scanned assessments (≤100 newest) that lack a default-method "
            "outcome label. Equals assessment_count minus labeled_assessment_count."
        ),
    )
    outcome_label_count: int = Field(ge=0)
    calibration_count: int = Field(ge=0)
    latest_component_source: str | None = Field(
        default=None,
        description=(
            "Component series source for the latest assessment (may be 'mixed' when "
            "cross-source fill was used). Null when no assessment."
        ),
    )
    latest_resolved_label_bar_source: str | None = Field(
        default=None,
        description=(
            "Observation source used (or that would be used) for Phase 13 label closes on "
            "the latest assessment. Prefers persisted label.bar_source when present."
        ),
    )
    mixed_component_source_assessment_count: int = Field(
        default=0,
        ge=0,
        description=(
            "Count of scanned assessments (≤100 newest) whose component_source is 'mixed'."
        ),
    )
    mixed_unlabeled_assessment_count: int = Field(
        default=0,
        ge=0,
        description=(
            "Count of scanned mixed-component assessments (≤100 newest) that lack a "
            "default-method outcome label."
        ),
    )
    mixed_labeled_assessment_count: int = Field(
        default=0,
        ge=0,
        description=(
            "Count of scanned mixed-component assessments (≤100 newest) that have a "
            "default-method outcome label. Equals mixed count minus unlabeled."
        ),
    )
    latest_mixed_label_bar_source: str | None = Field(
        default=None,
        description=(
            "bar_source from the newest mixed-component assessment that has a persisted "
            "outcome label. Null when none of the scanned mixed assessments are labeled."
        ),
    )
    most_recent_labeled_assessment_id: int | None = Field(
        default=None,
        description=(
            "Assessment id of the newest scanned assessment (≤100) that has a default-method "
            "outcome label. Null when none labeled. Distinct from latest_assessment when the "
            "absolute newest snapshot is still unlabeled."
        ),
    )
    most_recent_labeled_outcome_label: OutcomeLabelResponse | None = Field(
        default=None,
        description=(
            "Newest default-method outcome label among the ≤100 scan. Equals "
            "latest_outcome_label when the absolute latest assessment is labeled; otherwise "
            "the label from most_recent_labeled_assessment_id. Never invented."
        ),
    )
    latest_coverage_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "coverage_confidence from the latest assessment. Null when no assessment. "
            "Distinct from probability_confidence; never invented."
        ),
    )
    latest_research_index: float | None = Field(
        default=None,
        description=(
            "research_index from latest assessment components when present and numeric. "
            "Null when no assessment or the component is missing/non-numeric. Never invented."
        ),
    )
    detail: str
