"""FastAPI application factory and ASGI entrypoint."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aegis.api.routers.auth import router as auth_router
from aegis.api.routers.health import router as health_router
from aegis.api.routers.market_data import router as market_data_router
from aegis.api.routers.research import router as research_router
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
            "Decision-support backend for AEGIS 3.0. Phase 6: research-only assessments "
            "over stored daily bars (authenticated /research routes). Never places or "
            "transmits live orders; assessments are research-only, not actionable advice."
        ),
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Accept"],
    )
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(market_data_router)
    app.include_router(watchlist_router)
    app.include_router(research_router)
    # Available before lifespan runs so unit tests (and cookie helpers) can read settings
    # without starting Redis/Postgres.
    app.state.settings = resolved_settings
    return app


app = create_app()
