"""Response schemas for research outcome label endpoints (Phase 13, ADR-0014)."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


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
