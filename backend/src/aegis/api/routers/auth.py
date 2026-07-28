"""Operator authentication endpoints (Phase 4, see ADR-0005).

Issues an httpOnly session cookie backed by Redis. No OAuth, JWT, MFA, or multi-role
authorization. Passwords are never logged.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from aegis.api.dependencies import get_operator_repository, get_session_store, require_operator
from aegis.api.schemas.auth import LoginRequest, OperatorMeResponse
from aegis.domain.auth_passwords import verify_password
from aegis.persistence.models import Operator
from aegis.persistence.repositories.operators import OperatorRepository
from aegis.persistence.sessions import SessionStore

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_session_cookie(response: Response, request: Request, session_id: str) -> None:
    settings = request.app.state.settings
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_id,
        max_age=settings.session_ttl_seconds,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )


def _clear_session_cookie(response: Response, request: Request) -> None:
    settings = request.app.state.settings
    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
        secure=settings.session_cookie_secure,
        httponly=True,
        samesite="lax",
    )


@router.post("/login", response_model=OperatorMeResponse)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    repository: OperatorRepository = Depends(get_operator_repository),
    session_store: SessionStore = Depends(get_session_store),
) -> OperatorMeResponse:
    """Authenticate with username/password and set the session cookie."""

    settings = request.app.state.settings
    await repository.ensure_seeded(settings.operator_username, settings.operator_password)

    operator = await repository.get_by_username(body.username)
    if operator is None or not verify_password(body.password, operator.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid username or password",
        )

    session_id = await session_store.create(operator.id, operator.username)
    _set_session_cookie(response, request, session_id)
    return OperatorMeResponse(username=operator.username)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    session_store: SessionStore = Depends(get_session_store),
) -> None:
    """Delete the Redis session (if present) and clear the session cookie."""

    settings = request.app.state.settings
    session_id = request.cookies.get(settings.session_cookie_name)
    if session_id:
        await session_store.delete(session_id)
    _clear_session_cookie(response, request)


@router.get("/me", response_model=OperatorMeResponse)
async def me(operator: Operator = Depends(require_operator)) -> OperatorMeResponse:
    """Return the currently authenticated operator."""

    return OperatorMeResponse(username=operator.username)
