"""Scheduled ingestion coordination: acquire a distributed lock, then run one ingestion cycle.

Framework-free per the domain module boundary in ``docs/architecture/overview.md``: this
module depends only on the ``Protocol`` interfaces below, never on a concrete Redis client,
database session, or scheduler library. ``aegis.api.scheduler`` wires the real objects into
it, mirroring how ``aegis.api.dependencies`` wires ``MarketDataIngestionService`` for the
on-demand path. See ``docs/architecture/decisions/0003-phase-2-scheduled-watchlist.md`` and
``docs/architecture/decisions/0009-phase-8-scheduled-research.md`` (optional post-ingest
research inside the same lock).
"""

from __future__ import annotations

import logging
from typing import Protocol

from aegis.domain.market_data_ingestion import IngestionRunResult
from aegis.domain.scheduled_research import ResearchAssessor, run_research_after_ingest

logger = logging.getLogger(__name__)

_LOCK_VALUE = "locked"


class DistributedLock(Protocol):
    """The minimal Redis-shaped locking interface required for coordination."""

    async def set(self, name: str, value: str, *, nx: bool, ex: int) -> object:
        """Set ``name`` to ``value`` only if it does not already exist (``nx``), expiring
        after ``ex`` seconds. Returns a truthy value if the key was set, falsy otherwise."""
        ...

    async def delete(self, *names: str) -> object:
        """Delete the given key(s)."""
        ...


class WatchlistSource(Protocol):
    """The watchlist boundary required by the scheduled ingestion cycle."""

    async def ensure_seeded(self, seed_symbols: list[str]) -> None:
        """Seed the watchlist from ``seed_symbols`` if it is currently completely empty."""
        ...

    async def list_active(self) -> list[str]:
        """Return every currently active symbol."""
        ...


class IngestionRunner(Protocol):
    """The ingestion boundary required by the scheduled ingestion cycle."""

    async def run(self, symbols: list[str]) -> IngestionRunResult:
        """Ingest daily bars for every symbol in ``symbols``."""
        ...


async def run_locked_ingestion_cycle(
    *,
    redis_client: DistributedLock,
    lock_key: str,
    lock_ttl_seconds: int,
    watchlist: WatchlistSource,
    seed_symbols: list[str],
    ingestion_service: IngestionRunner,
    research_service: ResearchAssessor | None = None,
) -> IngestionRunResult | None:
    """Run one ingestion cycle over the active watchlist, guarded by a distributed lock.

    Returns ``None`` (running nothing) if another process already holds the lock, so multiple
    backend replicas can never run overlapping ingestion cycles. The lock is always released
    afterward, even if ingestion raises; in the worst case (a crash before release), ``ex``
    still bounds how long the lock can be held.

    When ``research_service`` is provided (Phase 8), research assessments run **inside the
    same lock** after ingest succeeds and before release, using stored bars only. Pass
    ``None`` when ``AEGIS_RESEARCH_SCHEDULE_AFTER_INGEST_ENABLED`` is false.
    """

    acquired = await redis_client.set(lock_key, _LOCK_VALUE, nx=True, ex=lock_ttl_seconds)
    if not acquired:
        logger.info("scheduled_ingestion_skipped_lock_held", extra={"lock_key": lock_key})
        return None

    try:
        await watchlist.ensure_seeded(seed_symbols)
        symbols = await watchlist.list_active()
        run_result = await ingestion_service.run(symbols)
        logger.info(
            "scheduled_ingestion_run_completed",
            extra={
                "symbol_count": len(symbols),
                "stored_total": sum(result.stored_count for result in run_result.results),
                "rejected_total": sum(result.rejected_count for result in run_result.results),
                "errored_symbols": [
                    result.symbol for result in run_result.results if result.error is not None
                ],
            },
        )
        if research_service is not None:
            await run_research_after_ingest(symbols, research_service)
        return run_result
    finally:
        try:
            await redis_client.delete(lock_key)
        except Exception:  # noqa: BLE001 - best-effort release; `ex` still bounds the lock.
            logger.warning("scheduled_ingestion_lock_release_failed", extra={"lock_key": lock_key})
