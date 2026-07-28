"""Readiness endpoint contract: 200 only when every dependency is reachable, else typed 503."""

from __future__ import annotations

from httpx import ASGITransport, AsyncClient

from aegis.api.dependencies import check_database_ready, check_redis_ready
from aegis.api.main import create_app
from aegis.config.settings import Settings


def _client_with_dependency_overrides(
    *, database_ready: bool, redis_ready: bool
) -> AsyncClient:
    app = create_app(settings=Settings(environment="test"))
    app.dependency_overrides[check_database_ready] = lambda: database_ready
    app.dependency_overrides[check_redis_ready] = lambda: redis_ready
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


async def test_ready_returns_200_when_all_dependencies_healthy() -> None:
    async with _client_with_dependency_overrides(
        database_ready=True, redis_ready=True
    ) as client:
        response = await client.get("/ready")

    assert response.status_code == 200
    body = response.json()
    assert body == {"status": "ready", "checks": {"database": "ok", "redis": "ok"}}


async def test_ready_returns_503_when_database_unavailable() -> None:
    async with _client_with_dependency_overrides(
        database_ready=False, redis_ready=True
    ) as client:
        response = await client.get("/ready")

    assert response.status_code == 503
    body = response.json()
    assert body == {
        "status": "unavailable",
        "checks": {"database": "unavailable", "redis": "ok"},
    }


async def test_ready_returns_503_when_redis_unavailable() -> None:
    async with _client_with_dependency_overrides(
        database_ready=True, redis_ready=False
    ) as client:
        response = await client.get("/ready")

    assert response.status_code == 503
    body = response.json()
    assert body == {
        "status": "unavailable",
        "checks": {"database": "ok", "redis": "unavailable"},
    }


async def test_ready_returns_503_when_all_dependencies_unavailable() -> None:
    async with _client_with_dependency_overrides(
        database_ready=False, redis_ready=False
    ) as client:
        response = await client.get("/ready")

    assert response.status_code == 503
    body = response.json()
    assert body == {
        "status": "unavailable",
        "checks": {"database": "unavailable", "redis": "unavailable"},
    }


async def test_ready_response_never_leaks_connection_details() -> None:
    async with _client_with_dependency_overrides(
        database_ready=False, redis_ready=False
    ) as client:
        response = await client.get("/ready")

    assert "postgresql" not in response.text
    assert "redis://" not in response.text
    assert "@localhost" not in response.text
