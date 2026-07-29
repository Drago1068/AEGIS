"""Request/response schemas for research assessment endpoints (Phase 6)."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ResearchAssessmentResponse(BaseModel):
    """A research-only assessment snapshot.

    ``probability_confidence`` is always null in Phase 6 (not calibrated). ``state`` is
    always ``research_only``. See ADR-0007.
    """

    model_config = ConfigDict(from_attributes=True)

    symbol: str
    method_id: str
    method_version: int
    state: str
    as_of_trading_date: date
    event_time: datetime
    computed_at: datetime
    coverage_confidence: float = Field(ge=0.0, le=1.0)
    probability_confidence: float | None = None
    components: dict[str, float]
    schema_version: int
    input_source: str
    lookback_start_date: date
    lookback_end_date: date
    bar_count: int
