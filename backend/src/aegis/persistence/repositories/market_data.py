"""Repository for stored daily bar observations.

Structurally satisfies ``aegis.domain.market_data_ingestion.DailyBarRepository`` without either
module importing the other, per the persistence/domain boundary in
``docs/architecture/overview.md``.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, time

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from aegis.persistence.models import MarketDailyBarObservation
from aegis.providers.market_data import DailyBar

_UNIQUE_CONSTRAINT_NAME = "uq_market_daily_bar_source_symbol_event_time"


class MarketDailyBarRepository:
    """SQLAlchemy-backed storage for daily bar observations (see ``persistence.models``)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def existing_trading_dates(self, source: str, symbol: str) -> set[date]:
        """Return every trading date already stored for ``(source, symbol)``."""

        stmt = select(MarketDailyBarObservation.trading_date).where(
            MarketDailyBarObservation.source == source,
            MarketDailyBarObservation.symbol == symbol,
        )
        result = await self._session.execute(stmt)
        return set(result.scalars().all())

    async def save_many(self, source: str, bars: list[DailyBar]) -> int:
        """Insert ``bars``, skipping any that already exist for their ``(symbol, trading_date)``.

        Uses ``INSERT ... ON CONFLICT DO NOTHING`` against the unique constraint so a
        concurrent or repeated ingestion run cannot create duplicate rows (idempotent skip,
        not a correction; see ADR-0002). Returns the number of rows actually inserted.
        """

        if not bars:
            return 0

        values = [
            {
                "source": source,
                "symbol": bar.symbol,
                "trading_date": bar.trading_date,
                "event_time": _session_close_placeholder(bar.trading_date),
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume,
                "raw_payload": bar.raw_payload,
            }
            for bar in bars
        ]

        stmt = (
            pg_insert(MarketDailyBarObservation)
            .values(values)
            .on_conflict_do_nothing(constraint=_UNIQUE_CONSTRAINT_NAME)
            .returning(MarketDailyBarObservation.id)
        )
        result = await self._session.execute(stmt)
        inserted_ids = result.scalars().all()
        await self._session.commit()
        return len(inserted_ids)

    async def list_recent(
        self,
        symbol: str,
        limit: int,
        *,
        sources: list[str] | None = None,
    ) -> list[MarketDailyBarObservation]:
        """Return up to ``limit`` most recent stored bars for ``symbol``, newest first.

        When ``sources`` is provided, only rows whose ``source`` is in that list are
        returned (Phase 11 research multi-source reads).
        """

        stmt = select(MarketDailyBarObservation).where(
            MarketDailyBarObservation.symbol == symbol
        )
        if sources is not None:
            stmt = stmt.where(MarketDailyBarObservation.source.in_(sources))
        stmt = stmt.order_by(MarketDailyBarObservation.trading_date.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


def _session_close_placeholder(trading_date: date) -> datetime:
    """Midnight UTC on ``trading_date``.

    A precise per-calendar session-close timestamp (which varies by exchange and by daylight
    saving time) is deferred; this column exists today primarily as the TimescaleDB hypertable
    partitioning key. Computing it precisely would require this repository to depend on
    ``aegis.domain.calendars``, which the persistence/domain module boundary does not require
    for Phase 1.
    """

    return datetime.combine(trading_date, time.min, tzinfo=UTC)
