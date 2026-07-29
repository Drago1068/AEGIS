"""Response schemas for research probability calibration readiness (Phase 16)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CalibrationReadinessResponse(BaseModel):
    """Read-only corpus-gate diagnostics. Never invents probability_confidence."""

    model_config = ConfigDict(from_attributes=True)

    symbol: str
    status: str
    assessment_snapshot_id: int | None = None
    research_index: float | None = None
    corpus_count: int = Field(ge=0)
    bucket_count: int = Field(ge=0)
    min_corpus: int = Field(ge=1)
    min_bucket: int = Field(ge=1)
    index_bucket_width: float = Field(gt=0)
    calibration_method_id: str
    detail: str
