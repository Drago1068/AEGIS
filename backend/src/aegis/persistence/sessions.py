"""Redis-backed operator session store (Phase 4 httpOnly cookie sessions).

Session ids map to a small JSON payload (operator id + username) with a TTL matching
``AEGIS_SESSION_TTL_SECONDS``. See ADR-0005. Framework-free aside from the Redis client
passed in by the API layer.
"""

from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from typing import Protocol

from redis.asyncio import Redis

_SESSION_KEY_PREFIX = "aegis:session:"


@dataclass(frozen=True, slots=True)
class SessionData:
    """Minimal identity payload stored under a session id in Redis."""

    operator_id: int
    username: str


class SessionStore(Protocol):
    """Storage for opaque session ids issued as httpOnly cookies."""

    async def create(self, operator_id: int, username: str) -> str:
        """Create a session and return its opaque id."""
        ...

    async def get(self, session_id: str) -> SessionData | None:
        """Return session data, or ``None`` if missing/expired/invalid."""
        ...

    async def delete(self, session_id: str) -> None:
        """Delete a session id. Missing keys are ignored."""
        ...


def _session_key(session_id: str) -> str:
    return f"{_SESSION_KEY_PREFIX}{session_id}"


async def create_session(
    client: Redis,
    *,
    operator_id: int,
    username: str,
    ttl_seconds: int,
) -> str:
    """Create a new session in Redis and return the opaque session id.

    The id is a URL-safe random token suitable for an httpOnly cookie value.
    """

    session_id = secrets.token_urlsafe(32)
    payload = json.dumps({"operator_id": operator_id, "username": username})
    await client.set(  # pyright: ignore[reportUnknownMemberType]
        _session_key(session_id), payload, ex=ttl_seconds
    )
    return session_id


async def get_session(client: Redis, session_id: str) -> SessionData | None:
    """Return session data for ``session_id``, or ``None`` if missing/expired/invalid."""

    raw = await client.get(_session_key(session_id))  # pyright: ignore[reportUnknownMemberType]
    if raw is None:
        return None

    text = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)

    try:
        data = json.loads(text)
        operator_id = int(data["operator_id"])
        username = str(data["username"])
    except (TypeError, ValueError, KeyError, json.JSONDecodeError):
        return None

    return SessionData(operator_id=operator_id, username=username)


async def delete_session(client: Redis, session_id: str) -> None:
    """Delete ``session_id`` from Redis. Missing keys are ignored."""

    await client.delete(_session_key(session_id))  # pyright: ignore[reportUnknownMemberType]


class RedisSessionStore:
    """``SessionStore`` implementation backed by the process Redis client."""

    def __init__(self, client: Redis, ttl_seconds: int) -> None:
        self._client = client
        self._ttl_seconds = ttl_seconds

    async def create(self, operator_id: int, username: str) -> str:
        return await create_session(
            self._client,
            operator_id=operator_id,
            username=username,
            ttl_seconds=self._ttl_seconds,
        )

    async def get(self, session_id: str) -> SessionData | None:
        return await get_session(self._client, session_id)

    async def delete(self, session_id: str) -> None:
        await delete_session(self._client, session_id)
