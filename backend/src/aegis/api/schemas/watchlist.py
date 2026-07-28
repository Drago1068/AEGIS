"""Request/response schemas for the watchlist management endpoints."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from aegis.domain.watchlist import normalize_symbol


class WatchlistSymbolResponse(BaseModel):
    """A single watchlist entry."""

    model_config = ConfigDict(from_attributes=True)

    symbol: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class WatchlistAddRequest(BaseModel):
    """Request body for ``POST /watchlist``."""

    symbol: str

    @field_validator("symbol")
    @classmethod
    def _normalize(cls, value: str) -> str:
        return normalize_symbol(value)
