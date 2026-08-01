"""Request/response schemas for the market data ingestion and read endpoints."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

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


class IngestionRunResponse(BaseModel):
    """Response for ``POST /market-data/ingest``."""

    model_config = ConfigDict(from_attributes=True)

    results: list[IngestionSymbolResult]
