"""Shared construction of :class:`~aegis.domain.market_data_ingestion.MarketDataIngestionService`.

Keeps FastAPI dependencies and the scheduler on one wiring path so primary/secondary
selection cannot diverge (ADR-0011).
"""

from __future__ import annotations

from decimal import Decimal

import httpx

from aegis.config.settings import Settings
from aegis.domain.market_data_ingestion import DailyBarRepository, MarketDataIngestionService
from aegis.providers.registry import build_daily_bar_provider


def build_market_data_ingestion_service(
    settings: Settings,
    client: httpx.AsyncClient,
    repository: DailyBarRepository,
) -> MarketDataIngestionService:
    """Wire primary (and optional secondary) daily-bar providers into the ingestion service."""

    primary = build_daily_bar_provider(settings.daily_bar_primary_source, settings, client)
    secondary = None
    secondary_source = settings.daily_bar_secondary_source
    if secondary_source is not None:
        secondary = build_daily_bar_provider(secondary_source, settings, client)

    return MarketDataIngestionService(
        primary,
        repository,
        source=settings.daily_bar_primary_source,
        secondary_provider=secondary,
        secondary_source=secondary_source,
        calendar_name=settings.exchange_calendar_name,
        max_latest_bar_staleness_trading_days=settings.max_latest_bar_staleness_trading_days,
        correction_price_epsilon=Decimal(str(settings.market_data_correction_price_epsilon)),
    )
