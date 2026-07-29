"""Unit tests for the locked scheduled-ingestion cycle, using fake doubles (no real I/O)."""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from aegis.domain.market_data_ingestion import IngestionRunResult, SymbolIngestionResult
from aegis.domain.research_assessment import (
    METHOD_ID,
    STATE_RESEARCH_ONLY,
    ResearchAssessmentReason,
    ResearchAssessmentSnapshotData,
    ResearchAssessmentUnavailableError,
)
from aegis.domain.scheduled_ingestion import run_locked_ingestion_cycle

_LOCK_KEY = "test:lock"
_LOCK_TTL = 60


class FakeRedis:
    def __init__(self, *, already_locked: bool = False) -> None:
        self.is_locked = already_locked
        self.set_calls: list[tuple[str, str, bool, int]] = []
        self.delete_calls: list[str] = []

    async def set(self, name: str, value: str, *, nx: bool, ex: int) -> bool:
        self.set_calls.append((name, value, nx, ex))
        if self.is_locked:
            return False
        self.is_locked = True
        return True

    async def delete(self, *names: str) -> int:
        self.delete_calls.extend(names)
        self.is_locked = False
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


class FakeResearchService:
    def __init__(self) -> None:
        self.assess_calls: list[str] = []
        self.lock_held_during_assess: bool | None = None
        self._redis: FakeRedis | None = None

    def bind_redis(self, redis_client: FakeRedis) -> None:
        self._redis = redis_client

    async def assess(self, symbol: str) -> ResearchAssessmentSnapshotData:
        self.assess_calls.append(symbol)
        if self._redis is not None:
            self.lock_held_during_assess = self._redis.is_locked
        return ResearchAssessmentSnapshotData(
            symbol=symbol,
            method_id=METHOD_ID,
            method_version=1,
            state=STATE_RESEARCH_ONLY,
            as_of_trading_date=date(2024, 1, 26),
            event_time=datetime(2024, 1, 26, 23, 59, 59, tzinfo=UTC),
            computed_at=datetime(2024, 1, 26, 18, 0, tzinfo=UTC),
            coverage_confidence=0.9,
            probability_confidence=None,
            components={
                "total_return_20": 0.1,
                "realized_vol_20": 0.2,
                "research_index": 0.46,
            },
            schema_version=1,
            input_source="alpha_vantage",
            lookback_start_date=date(2023, 12, 27),
            lookback_end_date=date(2024, 1, 26),
            bar_count=20,
        )


def _run_result(symbol: str = "AAPL") -> IngestionRunResult:
    return IngestionRunResult(
        results=[
            SymbolIngestionResult(
                symbol=symbol,
                stored_count=1,
                skipped_existing_count=0,
                corrected_count=0,
                rejected_count=0,
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
    research = FakeResearchService()

    result = await run_locked_ingestion_cycle(
        redis_client=redis_client,
        lock_key=_LOCK_KEY,
        lock_ttl_seconds=_LOCK_TTL,
        watchlist=watchlist,
        seed_symbols=[],
        ingestion_service=service,
        research_service=research,
    )

    assert result is None
    assert service.requested_symbols is None
    assert watchlist.ensure_seeded_calls == []
    assert redis_client.delete_calls == []
    assert research.assess_calls == []


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


@pytest.mark.asyncio
async def test_research_runs_inside_lock_after_successful_ingest() -> None:
    redis_client = FakeRedis()
    watchlist = FakeWatchlist(["AAPL", "MSFT"])
    service = FakeIngestionService(_run_result())
    research = FakeResearchService()
    research.bind_redis(redis_client)

    result = await run_locked_ingestion_cycle(
        redis_client=redis_client,
        lock_key=_LOCK_KEY,
        lock_ttl_seconds=_LOCK_TTL,
        watchlist=watchlist,
        seed_symbols=["AAPL"],
        ingestion_service=service,
        research_service=research,
    )

    assert result is not None
    assert research.assess_calls == ["AAPL", "MSFT"]
    assert research.lock_held_during_assess is True
    assert redis_client.delete_calls == [_LOCK_KEY]
    assert redis_client.is_locked is False


@pytest.mark.asyncio
async def test_research_not_run_when_service_omitted() -> None:
    redis_client = FakeRedis()
    watchlist = FakeWatchlist(["AAPL"])
    service = FakeIngestionService(_run_result())

    result = await run_locked_ingestion_cycle(
        redis_client=redis_client,
        lock_key=_LOCK_KEY,
        lock_ttl_seconds=_LOCK_TTL,
        watchlist=watchlist,
        seed_symbols=[],
        ingestion_service=service,
        research_service=None,
    )

    assert result is not None
    assert redis_client.delete_calls == [_LOCK_KEY]


@pytest.mark.asyncio
async def test_research_fail_closed_still_releases_lock() -> None:
    redis_client = FakeRedis()
    watchlist = FakeWatchlist(["AAPL"])
    service = FakeIngestionService(_run_result())

    class AlwaysUnavailableResearch:
        async def assess(self, symbol: str) -> ResearchAssessmentSnapshotData:
            raise ResearchAssessmentUnavailableError(
                ResearchAssessmentReason.STALE_LATEST_BAR,
                "stale",
            )

    result = await run_locked_ingestion_cycle(
        redis_client=redis_client,
        lock_key=_LOCK_KEY,
        lock_ttl_seconds=_LOCK_TTL,
        watchlist=watchlist,
        seed_symbols=[],
        ingestion_service=service,
        research_service=AlwaysUnavailableResearch(),
    )

    assert result is not None
    assert redis_client.delete_calls == [_LOCK_KEY]
