"""Request/response schemas for the market data ingestion and read endpoints."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from aegis.domain.market_data_ingestion import fetch_fallback_label_from_payload
from aegis.domain.market_data_validation import RejectionReason


class DailyBarResponse(BaseModel):
    """A single stored daily OHLCV observation."""

    model_config = ConfigDict(from_attributes=True)

    source: str
    symbol: str
    trading_date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    data_quality: str
    schema_version: int
    ingested_at: datetime
    fetch_fallback: str | None = Field(
        default=None,
        description=(
            "aegis_fetch_fallback from this observation's raw_payload "
            "(e.g. full_to_compact). Null when absent. Never invents closes; "
            "does not expose unrelated raw provider secrets."
        ),
    )

    @classmethod
    def from_observation(cls, bar: Any) -> DailyBarResponse:
        """Build a response from a stored observation without exposing raw_payload."""

        base = cls.model_validate(bar)
        return base.model_copy(
            update={"fetch_fallback": fetch_fallback_label_from_payload(bar.raw_payload)}
        )


class IngestionSymbolResult(BaseModel):
    """Per-symbol outcome of one ingestion run."""

    model_config = ConfigDict(from_attributes=True)

    symbol: str
    stored_count: int
    skipped_existing_count: int
    corrected_count: int
    rejected_count: int
    rejections: dict[RejectionReason, int]
    error: str | None = None
    latest_trading_date: date | None = None
    latest_trading_date_source: str | None = None
    primary_latest_trading_date: date | None = None
    # ``full_to_compact`` when AV compact fallback supplied primary bars; else null.
    primary_fetch_fallback: str | None = None


class IngestionRunResponse(BaseModel):
    """Response for ``POST /market-data/ingest``."""

    model_config = ConfigDict(from_attributes=True)

    results: list[IngestionSymbolResult]
