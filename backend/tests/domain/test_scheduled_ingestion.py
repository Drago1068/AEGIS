"""Unit tests for the locked scheduled-ingestion cycle, using fake doubles (no real I/O)."""

from __future__ import annotations

import pytest

from aegis.domain.market_data_ingestion import IngestionRunResult, SymbolIngestionResult
from aegis.domain.scheduled_ingestion import run_locked_ingestion_cycle

_LOCK_KEY = "test:lock"
_LOCK_TTL = 60


class FakeRedis:
    def __init__(self, *, already_locked: bool = False) -> None:
        self._locked = already_locked
        self.set_calls: list[tuple[str, str, bool, int]] = []
        self.delete_calls: list[str] = []

    async def set(self, name: str, value: str, *, nx: bool, ex: int) -> bool:
        self.set_calls.append((name, value, nx, ex))
        if self._locked:
            return False
        self._locked = True
        return True

    async def delete(self, *names: str) -> int:
        self.delete_calls.extend(names)
        self._locked = False
        return len(names)


class FakeWatchlist:
    def __init__(self, active: list[str]) -> None:
        self._active = active
        self.ensure_seeded_calls: list[list[str]] = []

    async def ensure_seeded(self, seed_symbols: list[str]) -> None:
        self.ensure_seeded_calls.append(seed_symbols)

    async def list_active(self) -> list[str]:
        return self._active


class FakeIngestionService:
    def __init__(self, result: IngestionRunResult) -> None:
        self._result = result
        self.requested_symbols: list[str] | None = None

    async def run(self, symbols: list[str]) -> IngestionRunResult:
        self.requested_symbols = symbols
        return self._result


def _run_result(symbol: str = "AAPL") -> IngestionRunResult:
    return IngestionRunResult(
        results=[
            SymbolIngestionResult(
                symbol=symbol, stored_count=1, skipped_existing_count=0, rejected_count=0
            )
        ]
    )


@pytest.mark.asyncio
async def test_lock_free_runs_ingestion_once_and_releases_lock() -> None:
    redis_client = FakeRedis()
    watchlist = FakeWatchlist(["AAPL", "MSFT"])
    service = FakeIngestionService(_run_result())

    result = await run_locked_ingestion_cycle(
        redis_client=redis_client,
        lock_key=_LOCK_KEY,
        lock_ttl_seconds=_LOCK_TTL,
        watchlist=watchlist,
        seed_symbols=["AAPL"],
        ingestion_service=service,
    )

    assert result is not None
    assert service.requested_symbols == ["AAPL", "MSFT"]
    assert watchlist.ensure_seeded_calls == [["AAPL"]]
    assert redis_client.set_calls == [(_LOCK_KEY, "locked", True, _LOCK_TTL)]
    assert redis_client.delete_calls == [_LOCK_KEY]


@pytest.mark.asyncio
async def test_lock_held_skips_the_run_entirely() -> None:
    redis_client = FakeRedis(already_locked=True)
    watchlist = FakeWatchlist(["AAPL"])
    service = FakeIngestionService(_run_result())

    result = await run_locked_ingestion_cycle(
        redis_client=redis_client,
        lock_key=_LOCK_KEY,
        lock_ttl_seconds=_LOCK_TTL,
        watchlist=watchlist,
        seed_symbols=[],
        ingestion_service=service,
    )

    assert result is None
    assert service.requested_symbols is None
    assert watchlist.ensure_seeded_calls == []
    assert redis_client.delete_calls == []


@pytest.mark.asyncio
async def test_lock_is_released_even_if_ingestion_raises() -> None:
    redis_client = FakeRedis()
    watchlist = FakeWatchlist(["AAPL"])

    class RaisingIngestionService:
        async def run(self, symbols: list[str]) -> IngestionRunResult:
            raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        await run_locked_ingestion_cycle(
            redis_client=redis_client,
            lock_key=_LOCK_KEY,
            lock_ttl_seconds=_LOCK_TTL,
            watchlist=watchlist,
            seed_symbols=[],
            ingestion_service=RaisingIngestionService(),
        )

    assert redis_client.delete_calls == [_LOCK_KEY]
