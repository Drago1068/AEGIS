"""FastAPI dependency providers for readiness checks.

These are defined as separate, overridable dependencies (rather than being called directly
inside the router) so unit tests can substitute fakes for each dependency independently via
``app.dependency_overrides``, covering both the available and unavailable outcome for each
dependency without a real database or Redis instance.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from aegis.domain.market_data_ingestion import MarketDataIngestionService
from aegis.persistence.cache import check_redis
from aegis.persistence.database import check_database
from aegis.persistence.repositories.market_data import MarketDailyBarRepository
from aegis.providers.alpha_vantage import AlphaVantageProvider

MARKET_DATA_SOURCE = "alpha_vantage"


async def check_database_ready(request: Request) -> bool:
    """Readiness dependency for PostgreSQL/TimescaleDB."""

    settings = request.app.state.settings
    engine = request.app.state.db_engine
    return await check_database(engine, settings.readiness_timeout_seconds)


async def check_redis_ready(request: Request) -> bool:
    """Readiness dependency for Redis."""

    settings = request.app.state.settings
    client = request.app.state.redis_client
    return await check_redis(client, settings.readiness_timeout_seconds)


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    """A request-scoped database session, closed when the request finishes."""

    session_factory = request.app.state.db_session_factory
    async with session_factory() as session:
        yield session


async def get_market_data_repository(
    session: AsyncSession = Depends(get_db_session),
) -> MarketDailyBarRepository:
    """A request-scoped repository for stored daily bar observations."""

    return MarketDailyBarRepository(session)


async def get_watchlist_symbols(request: Request) -> list[str]:
    """The configured ingestion watchlist (``AEGIS_WATCHLIST_SYMBOLS``)."""

    settings = request.app.state.settings
    return settings.watchlist


async def get_ingestion_service(
    request: Request,
    repository: MarketDailyBarRepository = Depends(get_market_data_repository),
) -> MarketDataIngestionService:
    """A request-scoped ingestion service wired to the configured provider and repository."""

    settings = request.app.state.settings
    provider = AlphaVantageProvider(settings, request.app.state.http_client)
    return MarketDataIngestionService(
        provider,
        repository,
        source=MARKET_DATA_SOURCE,
        calendar_name=settings.exchange_calendar_name,
        max_latest_bar_staleness_trading_days=settings.max_latest_bar_staleness_trading_days,
    )
