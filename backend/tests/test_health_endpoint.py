"""Liveness endpoint contract: always 200, no external dependency."""

from __future__ import annotations

from httpx import AsyncClient


async def test_health_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_health_does_not_require_app_lifespan(client: AsyncClient) -> None:
    """The test ``client`` fixture never runs the app lifespan, so app.state.db_engine and
    app.state.redis_client are never set. If ``/health`` touched either, this would raise
    and return a 500. A 200 here is direct evidence ``/health`` performs no dependency I/O.
    """

    response = await client.get("/health")

    assert response.status_code == 200
