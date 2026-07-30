"""Response schemas for research outcome label endpoints (Phase 13/43)."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class OutcomeLabelResponse(BaseModel):
    """Forward-return outcome labels for one assessment snapshot (evidence only)."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    assessment_snapshot_id: int
    symbol: str
    label_method_id: str
    label_method_version: int
    state: str
    as_of_trading_date: date
    computed_at: datetime
    labels: dict[str, float]
    label_end_dates: dict[str, str]
    schema_version: int
    bar_source: str


class OutcomeLabelBackfillItem(BaseModel):
    """Per-assessment outcome from a historical label backfill pass (Phase 43)."""

    symbol: str
    assessment_snapshot_id: int
    persisted: bool
    reason: str | None = None
    detail: str | None = None


class OutcomeLabelBackfillResponse(BaseModel):
    """Summary of research-only outcome-label backfill for one symbol (ADR-0044)."""

    symbol: str
    assessment_count: int = Field(ge=0)
    persisted_count: int = Field(ge=0)
    skipped_count: int = Field(ge=0)
    outcomes: list[OutcomeLabelBackfillItem] = Field(
        default_factory=lambda: []  # typed via annotation
    )
    detail: str = (
        "Research-only outcome-label backfill — not advice; skips are fail-closed, "
        "never invent confidence."
    )
