"""Readiness-endpoint integration test against the real Docker Compose stack.

Scope (see `docs/architecture/decisions/0001-phase-0-tooling.md`, decision 6): this
test requires `postgres`, `redis`, and `backend` to already be up and reporting
healthy (`docker compose up -d`, then wait for `docker compose ps` to show
`healthy`). It exercises the real network path into the backend container,
unlike `backend/tests/test_ready_endpoint.py`, which uses dependency overrides
against the in-process FastAPI app.

Only the healthy path is asserted here. The unavailable-dependency paths (503
responses) are already fully covered by the backend unit tests and are not
re-verified against real containers in Phase 0.
"""

from __future__ import annotations

import time

import httpx

READY_TIMEOUT_SECONDS = 60.0
POLL_INTERVAL_SECONDS = 2.0
REQUEST_TIMEOUT_SECONDS = 5.0


def _wait_for_ready(url: str, timeout_seconds: float) -> httpx.Response:
    """Poll `url` until it returns HTTP 200 or the timeout elapses.

    Compose reports a container as "healthy" once its own health check passes,
    but a short additional grace period is tolerated here for the first
    request to land after that transition.
    """

    deadline = time.monotonic() + timeout_seconds
    last_response: httpx.Response | None = None
    last_error: httpx.HTTPError | None = None

    while time.monotonic() < deadline:
        try:
            last_response = httpx.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        except httpx.HTTPError as exc:
            last_error = exc
        else:
            if last_response.status_code == 200:
                return last_response
        time.sleep(POLL_INTERVAL_SECONDS)

    if last_response is not None:
        return last_response
    assert last_error is not None
    raise last_error


def test_health_endpoint_is_reachable(backend_base_url: str) -> None:
    response = httpx.get(f"{backend_base_url}/health", timeout=REQUEST_TIMEOUT_SECONDS)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_endpoint_reports_all_dependencies_healthy(backend_base_url: str) -> None:
    response = _wait_for_ready(f"{backend_base_url}/ready", READY_TIMEOUT_SECONDS)

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {"database": "ok", "redis": "ok"},
    }
