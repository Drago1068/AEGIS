"""Shared pytest fixtures for backend unit tests."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from aegis.api.main import create_app
from aegis.config.settings import Settings


@pytest.fixture
def settings() -> Settings:
    """Test settings. Never points at a real database/Redis instance."""

    return Settings(environment="test")


@pytest.fixture
async def client(settings: Settings) -> AsyncIterator[AsyncClient]:
    """An HTTP client for the app with no readiness dependencies overridden.

    Suitable for endpoints (like ``/health``) that must not touch app state. Tests that need
    ``/ready`` must build their own client with dependency overrides (see
    ``test_ready_endpoint.py``) since the app lifespan does not run under this transport.
    """

    app = create_app(settings=settings)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
