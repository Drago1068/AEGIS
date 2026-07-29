"""Response schemas for research probability calibration endpoints (Phase 18)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProbabilityCalibrationResponse(BaseModel):
    """Append-only research_calibration_v1 row (research-only; not trade advice)."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    assessment_snapshot_id: int
    symbol: str
    calibration_method_id: str
    calibration_method_version: int
    state: str
    computed_at: datetime
    probability_confidence: float = Field(ge=0.0, le=1.0)
    corpus_count: int = Field(ge=0)
    bucket_count: int = Field(ge=0)
    schema_version: int
