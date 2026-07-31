"""Response schema for symbol research evidence summary (Phase 22, ADR-0023)."""

from __future__ import annotations

from datetime import date, datetime

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
    most_recent_labeled_outcome_label_id: int | None = Field(
        default=None,
        ge=1,
        description=(
            "id from most_recent_labeled_outcome_label when present. Null when no scan-labeled "
            "rows. Distinct from latest_outcome_label_id (null when absolute newest is "
            "unlabeled) and most_recent_labeled_assessment_id. Never invented."
        ),
    )
    most_recent_labeled_outcome_label_method_id: str | None = Field(
        default=None,
        description=(
            "label_method_id from most_recent_labeled_outcome_label when present. Null when no "
            "scan-labeled rows. Distinct from latest_outcome_label_method_id and "
            "assessment/calibration method ids. Never invented."
        ),
    )
    most_recent_labeled_outcome_label_method_version: int | None = Field(
        default=None,
        description=(
            "label_method_version from most_recent_labeled_outcome_label when present. Null when "
            "no scan-labeled rows. Distinct from latest_outcome_label_method_version and "
            "assessment/calibration method versions. Never invented."
        ),
    )
    most_recent_labeled_outcome_label_schema_version: int | None = Field(
        default=None,
        description=(
            "schema_version from most_recent_labeled_outcome_label when present. Null when no "
            "scan-labeled rows. Distinct from latest_outcome_label_schema_version and "
            "assessment/calibration schema versions. Never invented."
        ),
    )
    most_recent_labeled_outcome_label_state: str | None = Field(
        default=None,
        description=(
            "state from most_recent_labeled_outcome_label when present. Null when no "
            "scan-labeled rows. Distinct from latest_outcome_label_state and "
            "assessment/calibration states. Never invented."
        ),
    )
    most_recent_labeled_outcome_label_bar_source: str | None = Field(
        default=None,
        description=(
            "bar_source from most_recent_labeled_outcome_label when present. Null when no "
            "scan-labeled rows. Distinct from latest_outcome_label_bar_source and assessment "
            "input/source fields. Never invented."
        ),
    )
    most_recent_labeled_outcome_label_computed_at: datetime | None = Field(
        default=None,
        description=(
            "computed_at from most_recent_labeled_outcome_label when present. Null when no "
            "scan-labeled rows. Distinct from latest_outcome_label_computed_at and "
            "assessment/calibration computed_at. Never invented."
        ),
    )
    most_recent_labeled_outcome_label_as_of_trading_date: date | None = Field(
        default=None,
        description=(
            "as_of_trading_date from most_recent_labeled_outcome_label when present. Null when "
            "no scan-labeled rows. Distinct from latest_outcome_label_as_of_trading_date and "
            "assessment latest_as_of_trading_date. Never invented."
        ),
    )
    scan_labeled_freshness_lag_trading_days: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Exchange trading-day lag from most_recent_labeled_outcome_label_as_of_trading_date "
            "to latest_as_of_trading_date (strictly after labeled through latest inclusive). "
            "Null when either date is missing. Clamped to 0 if inverted. Never invented."
        ),
    )
    latest_assessment_is_label_ready: bool | None = Field(
        default=None,
        description=(
            "True when the latest assessment has stored forward-horizon closes needed to "
            "compute outcome labels (same gates as label backfill). Null when no latest "
            "assessment. Never invented."
        ),
    )
    latest_assessment_label_block_reason: str | None = Field(
        default=None,
        description=(
            "Fail-closed OutcomeLabelReason code when latest assessment is not label-ready "
            "(no_as_of_bar | insufficient_forward_bars). Null when no latest assessment or "
            "when label-ready. Never invented."
        ),
    )
    most_recent_labelable_as_of_trading_date: date | None = Field(
        default=None,
        description=(
            "as_of_trading_date of the newest scanned assessment that is label-ready with "
            "stored forward bars. Null when none are label-ready. Distinct from "
            "latest_as_of_trading_date and most_recent_labeled_outcome_label_as_of_trading_date. "
            "Never invented."
        ),
    )
    most_recent_unlabeled_labelable_as_of_trading_date: date | None = Field(
        default=None,
        description=(
            "as_of_trading_date of the newest scanned assessment that is unlabeled and "
            "label-ready (backfill next-target). Null when none. Distinct from "
            "most_recent_labelable_as_of_trading_date. Never invented."
        ),
    )
    scan_unlabeled_label_ready_count: int = Field(
        default=0,
        ge=0,
        description=(
            "Count of scanned assessments that are unlabeled and label-ready "
            "(backfill-candidate cardinality). Zero when none or empty scan. Never invented."
        ),
    )
    most_recent_unlabeled_assessment_id: int | None = Field(
        default=None,
        ge=1,
        description=(
            "Assessment id of the newest scanned assessment that has no default-method "
            "outcome label (unlabeled tip for drill-down). Null when none unlabeled. "
            "Distinct from most_recent_labeled_assessment_id and latest_assessment_id "
            "(equals latest only when latest is unlabeled). Never invented."
        ),
    )
    most_recent_unlabeled_as_of_trading_date: date | None = Field(
        default=None,
        description=(
            "as_of_trading_date of the newest scanned unlabeled assessment (same row as "
            "most_recent_unlabeled_assessment_id). Null when none unlabeled. Distinct from "
            "most_recent_unlabeled_labelable_as_of_trading_date and latest_as_of_trading_date. "
            "Never invented."
        ),
    )
    latest_assessment_forward_bar_shortfall: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Trading sessions of stored bars still needed before the latest assessment "
            "satisfies the max forward horizon (backfill unlock). 0 when label-ready; "
            "null when no assessment or no as_of bar. Never invented."
        ),
    )
    latest_assessment_required_label_end_date: date | None = Field(
        default=None,
        description=(
            "Trading date at which the max forward horizon for the latest assessment "
            "would unlock labeling (calendar projection from as_of). Null when no "
            "assessment or no as_of bar. Never invents closes."
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
    latest_as_of_trading_date: date | None = Field(
        default=None,
        description=(
            "as_of_trading_date from the latest assessment. Null when no assessment. "
            "Never invented."
        ),
    )
    latest_bar_count: int | None = Field(
        default=None,
        ge=0,
        description=(
            "bar_count from the latest assessment. Null when no assessment. Never invented."
        ),
    )
    latest_input_source: str | None = Field(
        default=None,
        description=(
            "input_source from the latest assessment (primary observation provenance). "
            "Null when no assessment. Distinct from latest_component_source (which may be "
            "'mixed'). Never invented."
        ),
    )
    latest_method_id: str | None = Field(
        default=None,
        description=(
            "method_id from the latest assessment. Null when no assessment. Never invented."
        ),
    )
    latest_method_version: int | None = Field(
        default=None,
        ge=1,
        description=(
            "method_version from the latest assessment. Null when no assessment. Never invented."
        ),
    )
    latest_lookback_end_date: date | None = Field(
        default=None,
        description=(
            "lookback_end_date from the latest assessment. Null when no assessment. "
            "Never invented."
        ),
    )
    latest_lookback_start_date: date | None = Field(
        default=None,
        description=(
            "lookback_start_date from the latest assessment. Null when no assessment. "
            "Never invented."
        ),
    )
    latest_schema_version: int | None = Field(
        default=None,
        ge=1,
        description=(
            "schema_version from the latest assessment. Null when no assessment. Never invented."
        ),
    )
    latest_computed_at: datetime | None = Field(
        default=None,
        description=(
            "computed_at from the latest assessment. Null when no assessment. Never invented."
        ),
    )
    latest_event_time: datetime | None = Field(
        default=None,
        description=(
            "event_time from the latest assessment. Null when no assessment. Never invented."
        ),
    )
    latest_probability_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "probability_confidence from the latest assessment when a calibration is attached. "
            "Null when no assessment or no calibrated probability. Distinct from "
            "latest_coverage_confidence; never invented."
        ),
    )
    latest_assessment_id: int | None = Field(
        default=None,
        ge=1,
        description=(
            "id from the latest assessment. Null when no assessment. Distinct from "
            "most_recent_labeled_assessment_id when the absolute newest snapshot is unlabeled. "
            "Never invented."
        ),
    )
    latest_outcome_label_id: int | None = Field(
        default=None,
        ge=1,
        description=(
            "id from latest_outcome_label when the latest assessment is labeled. Null when "
            "no label on the absolute newest assessment. Never invented."
        ),
    )
    latest_outcome_label_computed_at: datetime | None = Field(
        default=None,
        description=(
            "computed_at from latest_outcome_label when the latest assessment is labeled. "
            "Null when unlabeled. Distinct from assessment latest_computed_at and "
            "latest_calibration_computed_at. Never invented."
        ),
    )
    latest_outcome_label_method_id: str | None = Field(
        default=None,
        description=(
            "label_method_id from latest_outcome_label when the latest assessment is labeled. "
            "Null when unlabeled. Distinct from assessment latest_method_id and "
            "latest_calibration_method_id. Never invented."
        ),
    )
    latest_outcome_label_method_version: int | None = Field(
        default=None,
        ge=1,
        description=(
            "label_method_version from latest_outcome_label when the latest assessment is "
            "labeled. Null when unlabeled. Distinct from assessment latest_method_version and "
            "latest_calibration_method_version. Never invented."
        ),
    )
    latest_outcome_label_schema_version: int | None = Field(
        default=None,
        ge=1,
        description=(
            "schema_version from latest_outcome_label when the latest assessment is labeled. "
            "Null when unlabeled. Distinct from assessment latest_schema_version and "
            "latest_calibration_schema_version. Never invented."
        ),
    )
    latest_outcome_label_state: str | None = Field(
        default=None,
        description=(
            "state from latest_outcome_label when the latest assessment is labeled. Null when "
            "unlabeled. Expected research_only; distinct from summary state and "
            "latest_calibration_state. Never invented."
        ),
    )
    latest_outcome_label_bar_source: str | None = Field(
        default=None,
        description=(
            "bar_source from latest_outcome_label when the latest assessment is labeled. Null "
            "when unlabeled. Distinct from latest_resolved_label_bar_source (which may resolve "
            "without a label row) and latest_mixed_label_bar_source. Never invented."
        ),
    )
    latest_outcome_label_as_of_trading_date: date | None = Field(
        default=None,
        description=(
            "as_of_trading_date from latest_outcome_label when the latest assessment is labeled. "
            "Null when unlabeled. Distinct from assessment latest_as_of_trading_date. Never "
            "invented."
        ),
    )
    latest_calibration_id: int | None = Field(
        default=None,
        ge=1,
        description=(
            "id from latest_calibration when a calibration row is attached. Null when none. "
            "Never invented."
        ),
    )
    latest_calibration_horizon_key: str | None = Field(
        default=None,
        description=(
            "outcome_horizon_key from latest_calibration when present. Null when none. "
            "Never invented."
        ),
    )
    latest_calibration_computed_at: datetime | None = Field(
        default=None,
        description=(
            "computed_at from latest_calibration when present. Null when none. Distinct from "
            "assessment latest_computed_at. Never invented."
        ),
    )
    latest_calibration_corpus_count: int | None = Field(
        default=None,
        ge=0,
        description=(
            "corpus_count from latest_calibration when present. Null when none. Distinct from "
            "calibration_readiness corpus thresholds. Never invented."
        ),
    )
    latest_calibration_bucket_count: int | None = Field(
        default=None,
        ge=0,
        description=(
            "bucket_count from latest_calibration when present. Null when none. Distinct from "
            "calibration_readiness bucket thresholds. Never invented."
        ),
    )
    latest_calibration_method_id: str | None = Field(
        default=None,
        description=(
            "calibration_method_id from latest_calibration when present. Null when none. "
            "Distinct from assessment latest_method_id. Never invented."
        ),
    )
    latest_calibration_method_version: int | None = Field(
        default=None,
        ge=1,
        description=(
            "calibration_method_version from latest_calibration when present. Null when none. "
            "Distinct from assessment latest_method_version. Never invented."
        ),
    )
    latest_calibration_schema_version: int | None = Field(
        default=None,
        ge=1,
        description=(
            "schema_version from latest_calibration when present. Null when none. Distinct from "
            "assessment latest_schema_version. Never invented."
        ),
    )
    latest_calibration_state: str | None = Field(
        default=None,
        description=(
            "state from latest_calibration when present. Null when none. Expected research_only; "
            "never invented."
        ),
    )
    latest_calibration_probability_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "probability_confidence from latest_calibration when present. Null when none. "
            "Distinct from assessment latest_probability_confidence. Never invented."
        ),
    )
    latest_calibration_assessment_snapshot_id: int | None = Field(
        default=None,
        ge=1,
        description=(
            "assessment_snapshot_id from latest_calibration when present. Null when none. "
            "May differ from latest_assessment_id when newest assessment has no calibration. "
            "Never invented."
        ),
    )
    detail: str
