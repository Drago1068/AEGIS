"""Unit tests for scheduler lifespan wiring (start/stop only; no real trigger fires)."""

from __future__ import annotations

from aegis.api.main import create_app
from aegis.config.settings import Settings


async def test_scheduler_is_started_when_schedule_enabled() -> None:
    app = create_app(settings=Settings(environment="test", ingestion_schedule_enabled=True))

    async with app.router.lifespan_context(app):
        assert app.state.ingestion_scheduler is not None


async def test_scheduler_is_not_started_when_schedule_disabled() -> None:
    app = create_app(settings=Settings(environment="test", ingestion_schedule_enabled=False))

    async with app.router.lifespan_context(app):
        assert app.state.ingestion_scheduler is None
