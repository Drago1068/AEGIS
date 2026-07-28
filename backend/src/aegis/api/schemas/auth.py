"""Request/response schemas for operator authentication endpoints."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    """Request body for ``POST /auth/login``."""

    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)


class OperatorMeResponse(BaseModel):
    """Authenticated operator identity returned by ``GET /auth/me`` and login."""

    model_config = ConfigDict(from_attributes=True)

    username: str
