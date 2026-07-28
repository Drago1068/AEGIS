"""CORS configuration: allow-listed origins from settings receive Access-Control headers."""

from __future__ import annotations

from httpx import ASGITransport, AsyncClient

from aegis.api.main import create_app
from aegis.config.settings import Settings

_ORIGIN = "http://localhost:3000"
_OTHER_ORIGIN = "http://evil.example"


async def test_preflight_allows_configured_origin() -> None:
    app = create_app(
        settings=Settings(
            environment="test",
            cors_origins=_ORIGIN,
            ingestion_schedule_enabled=False,
        )
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.options(
            "/watchlist",
            headers={
                "Origin": _ORIGIN,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == _ORIGIN
    assert response.headers.get("access-control-allow-credentials") == "true"
    assert "POST" in response.headers.get("access-control-allow-methods", "")


async def test_preflight_rejects_unlisted_origin() -> None:
    app = create_app(
        settings=Settings(
            environment="test",
            cors_origins=_ORIGIN,
            ingestion_schedule_enabled=False,
        )
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.options(
            "/watchlist",
            headers={
                "Origin": _OTHER_ORIGIN,
                "Access-Control-Request-Method": "GET",
            },
        )

    assert "access-control-allow-origin" not in response.headers
