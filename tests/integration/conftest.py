"""Shared fixtures for cross-service integration tests.

These tests exercise a real, already-running `docker compose` stack (see
`docs/operations/local-development.md`). They do not start or stop containers
themselves; that is the responsibility of the caller (a developer running
`docker compose up -d`, or the CI `integration` job).
"""

from __future__ import annotations

import os

import pytest

DEFAULT_BACKEND_URL = "http://localhost:8000"


@pytest.fixture(scope="session")
def backend_base_url() -> str:
    """Base URL of the backend service under test.

    Overridable via `AEGIS_INTEGRATION_BACKEND_URL` so CI can target a
    differently-networked Compose stack without editing test code.
    """

    return os.environ.get("AEGIS_INTEGRATION_BACKEND_URL", DEFAULT_BACKEND_URL)
