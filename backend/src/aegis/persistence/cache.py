"""Redis client construction and cache health checks."""

from __future__ import annotations

import asyncio

from redis.asyncio import Redis

from aegis.config.settings import Settings


def create_redis_client(settings: Settings) -> Redis:
    """Create a new Redis async client from settings."""

    # redis-py's async client ships incomplete type stubs for `from_url`
    # (reportUnknownMemberType); the return type is annotated explicitly above instead.
    return Redis.from_url(settings.redis_url)  # pyright: ignore[reportUnknownMemberType]


async def check_redis(client: Redis, timeout_seconds: float) -> bool:
    """Return ``True`` if a PING against Redis succeeds within the timeout.

    Never raises: any exception (connection failure, timeout, auth failure) is treated as
    "not ready" rather than propagated, so callers can build a safe typed readiness response.
    """

    try:
        async with asyncio.timeout(timeout_seconds):
            # redis-py's async client ships incomplete type stubs for `ping`
            # (reportUnknownMemberType); the bool(...) coercion below makes the result type
            # explicit regardless.
            pong = await client.ping()  # pyright: ignore[reportUnknownMemberType]
        return bool(pong)
    except Exception:  # noqa: BLE001 - readiness checks must never raise
        return False
