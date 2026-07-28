"""Liveness (``/health``) and readiness (``/ready``) endpoints.

Contract (see ``docs/architecture/overview.md``):

- ``/health`` always returns 200 while the process is running and never depends on any
  external service.
- ``/ready`` returns 200 only when PostgreSQL/TimescaleDB and Redis are both reachable, and a
  typed 503 otherwise, naming which dependency failed without leaking connection details.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from aegis.api.dependencies import check_database_ready, check_redis_ready
from aegis.api.schemas.health import (
    DependencyStatus,
    HealthResponse,
    NotReadyResponse,
    ReadyResponse,
)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Process liveness. Performs no I/O and has no external dependency."""

    return HealthResponse()


@router.get(
    "/ready",
    response_model=ReadyResponse,
    responses={503: {"model": NotReadyResponse}},
)
async def ready(
    database_ready: bool = Depends(check_database_ready),
    redis_ready: bool = Depends(check_redis_ready),
) -> JSONResponse:
    """Process readiness, gated on PostgreSQL/TimescaleDB and Redis reachability."""

    checks = DependencyStatus(
        database="ok" if database_ready else "unavailable",
        redis="ok" if redis_ready else "unavailable",
    )

    if database_ready and redis_ready:
        body = ReadyResponse(checks=checks)
        return JSONResponse(status_code=200, content=body.model_dump())

    body = NotReadyResponse(checks=checks)
    return JSONResponse(status_code=503, content=body.model_dump())
