"""Response schemas for the liveness and readiness endpoints."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Liveness response. Always ``ok`` if the process can handle a request at all."""

    status: Literal["ok"] = "ok"


class DependencyStatus(BaseModel):
    """Per-dependency readiness status, never leaking connection details."""

    database: Literal["ok", "unavailable"]
    redis: Literal["ok", "unavailable"]


class ReadyResponse(BaseModel):
    """Returned with HTTP 200 when every dependency is reachable."""

    status: Literal["ready"] = "ready"
    checks: DependencyStatus


class NotReadyResponse(BaseModel):
    """Returned with HTTP 503 when at least one dependency is unreachable."""

    status: Literal["unavailable"] = "unavailable"
    checks: DependencyStatus
