"""Request/response schemas for research assessment endpoints (Phase 6 / 11)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ResearchAssessmentResponse(BaseModel):
    """A research-only assessment snapshot.

    ``probability_confidence`` is null when no Phase 15 calibration row exists; when present
    it is a bounded empirical value from ``research_calibration_v1`` (research-only, not
    trade advice). ``state`` is always ``research_only``. See ADR-0007, ADR-0012, and
    ADR-0016. ``components`` may include numeric research metrics and (method_version 2)
    provenance / factor breakdown fields.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    symbol: str
    method_id: str
    method_version: int
    state: str
    as_of_trading_date: date
    event_time: datetime
    computed_at: datetime
    coverage_confidence: float = Field(ge=0.0, le=1.0)
    probability_confidence: float | None = None
    components: dict[str, Any]
    schema_version: int
    input_source: str
    lookback_start_date: date
    lookback_end_date: date
    bar_count: int


class AssessmentBackfillItem(BaseModel):
    """Per-date outcome from a historical assessment backfill pass (Phase 45)."""

    symbol: str
    as_of_trading_date: date
    persisted: bool
    assessment_snapshot_id: int | None = None
    reason: str | None = None
    detail: str | None = None


class AssessmentBackfillResponse(BaseModel):
    """Summary of research-only assessment backfill for one symbol (ADR-0046)."""

    symbol: str
    candidate_count: int = Field(ge=0)
    persisted_count: int = Field(ge=0)
    skipped_count: int = Field(ge=0)
    outcomes: list[AssessmentBackfillItem] = Field(default_factory=lambda: [])
    detail: str = (
        "Research-only assessment backfill — not advice; skips are fail-closed, "
        "never invent confidence."
    )
