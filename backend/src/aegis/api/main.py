"""FastAPI application factory and ASGI entrypoint."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from aegis.api.routers.health import router as health_router
from aegis.api.routers.market_data import router as market_data_router
from aegis.api.routers.watchlist import router as watchlist_router
from aegis.api.scheduler import IngestionScheduler
from aegis.config.settings import Settings, get_settings
from aegis.persistence.cache import create_redis_client
from aegis.persistence.database import create_engine, create_session_factory


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI application.

    Accepts an optional explicit ``Settings`` instance so integration tests can point the
    app at a specific database/Redis instance without relying on process environment state.
    """

    resolved_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        app.state.settings = resolved_settings
        app.state.db_engine = create_engine(resolved_settings)
        app.state.db_session_factory = create_session_factory(app.state.db_engine)
        app.state.redis_client = create_redis_client(resolved_settings)
        app.state.http_client = httpx.AsyncClient()

        scheduler: IngestionScheduler | None = None
        if resolved_settings.ingestion_schedule_enabled:
            scheduler = IngestionScheduler(app, resolved_settings.ingestion_cron)
            scheduler.start()
        app.state.ingestion_scheduler = scheduler

        try:
            yield
        finally:
            if scheduler is not None:
                scheduler.shutdown()
            await app.state.db_engine.dispose()
            await app.state.redis_client.aclose()
            await app.state.http_client.aclose()

    app = FastAPI(
        title="AEGIS 3.0 Backend",
        version="0.1.0",
        description=(
            "Decision-support backend for AEGIS 3.0. Phase 2: scheduled market data "
            "ingestion (Alpha Vantage daily bars) over a database-backed watchlist. This "
            "service never places or transmits live orders."
        ),
        lifespan=lifespan,
    )
    app.include_router(health_router)
    app.include_router(market_data_router)
    app.include_router(watchlist_router)
    return app


app = create_app()
