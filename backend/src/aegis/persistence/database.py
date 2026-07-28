"""SQLAlchemy async engine construction and database health checks."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from aegis.config.settings import Settings


def create_engine(settings: Settings) -> AsyncEngine:
    """Create a new SQLAlchemy async engine from settings.

    A fresh engine is created per call rather than sharing a process-wide singleton by
    default, so tests can construct isolated engines. The FastAPI app wires a single engine
    into application state at startup.
    """

    return create_async_engine(settings.database_url, pool_pre_ping=True)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create a session factory bound to the given engine."""

    return async_sessionmaker(bind=engine, expire_on_commit=False)


@asynccontextmanager
async def _bounded(timeout_seconds: float) -> AsyncGenerator[None]:
    async with asyncio.timeout(timeout_seconds):
        yield


async def check_database(engine: AsyncEngine, timeout_seconds: float) -> bool:
    """Return ``True`` if a trivial query succeeds against the database within the timeout.

    Never raises: any exception (connection failure, timeout, auth failure) is treated as
    "not ready" rather than propagated, so callers can build a safe typed readiness response.
    """

    try:
        async with _bounded(timeout_seconds), engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True
    except Exception:  # noqa: BLE001 - readiness checks must never raise
        return False
