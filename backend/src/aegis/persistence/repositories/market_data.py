"""Repository for stored daily bar observations.

Structurally satisfies ``aegis.domain.market_data_ingestion.DailyBarRepository`` without either
module importing the other, per the persistence/domain module boundary in
``docs/architecture/overview.md``.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, time

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from aegis.domain.market_data_corrections import StoredBarSnapshot
from aegis.persistence.models import MarketDailyBarObservation
from aegis.providers.market_data import DailyBar

_OBSERVATION_KIND_INITIAL = "initial"
_OBSERVATION_KIND_CORRECTION = "correction"


class MarketDailyBarRepository:
    """SQLAlchemy-backed storage for daily bar observations (see ``persistence.models``)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_current_by_trading_dates(
        self,
        source: str,
        symbol: str,
        trading_dates: set[date],
    ) -> dict[date, StoredBarSnapshot]:
        """Return the current observation per trading date (latest ``ingested_at`` wins)."""

        if not trading_dates:
            return {}

        max_ingested = (
            select(
                MarketDailyBarObservation.trading_date,
                func.max(MarketDailyBarObservation.ingested_at).label("max_ingested_at"),
            )
            .where(
                MarketDailyBarObservation.source == source,
                MarketDailyBarObservation.symbol == symbol,
                MarketDailyBarObservation.trading_date.in_(trading_dates),
            )
            .group_by(MarketDailyBarObservation.trading_date)
            .subquery()
        )

        stmt = (
            select(MarketDailyBarObservation)
            .join(
                max_ingested,
                (
                    MarketDailyBarObservation.trading_date == max_ingested.c.trading_date
                )
                & (
                    MarketDailyBarObservation.ingested_at == max_ingested.c.max_ingested_at
                ),
            )
            .where(
                MarketDailyBarObservation.source == source,
                MarketDailyBarObservation.symbol == symbol,
            )
        )
        result = await self._session.execute(stmt)
        rows = list(result.scalars().all())

        snapshots: dict[date, StoredBarSnapshot] = {}
        for row in rows:
            snapshots[row.trading_date] = StoredBarSnapshot(
                id=row.id,
                trading_date=row.trading_date,
                open=row.open,
                high=row.high,
                low=row.low,
                close=row.close,
                volume=row.volume,
                data_quality=row.data_quality,
            )
        return snapshots

    async def save_many(self, source: str, bars: list[DailyBar]) -> int:
        """Insert ``initial`` observations for ``bars``. Returns rows inserted."""

        if not bars:
            return 0

        observations = [
            _observation_from_bar(source, bar, observation_kind=_OBSERVATION_KIND_INITIAL)
            for bar in bars
        ]
        self._session.add_all(observations)
        await self._session.commit()
        return len(observations)

    async def save_corrections(
        self,
        source: str,
        corrections: list[tuple[DailyBar, int]],
    ) -> int:
        """Insert ``correction`` rows that supersede prior observations."""

        if not corrections:
            return 0

        observations = [
            _observation_from_bar(
                source,
                bar,
                observation_kind=_OBSERVATION_KIND_CORRECTION,
                supersedes_observation_id=supersedes_id,
            )
            for bar, supersedes_id in corrections
        ]
        self._session.add_all(observations)
        await self._session.commit()
        return len(observations)

    async def list_recent(
        self,
        symbol: str,
        limit: int,
        *,
        sources: list[str] | None = None,
    ) -> list[MarketDailyBarObservation]:
        """Return up to ``limit`` most recent **current** bars for ``symbol``, newest first.

        For each ``(source, symbol, trading_date)``, only the row with the latest
        ``ingested_at`` is returned (ADR-0013).
        """

        max_ingested = (
            select(
                MarketDailyBarObservation.source,
                MarketDailyBarObservation.trading_date,
                func.max(MarketDailyBarObservation.ingested_at).label("max_ingested_at"),
            )
            .where(MarketDailyBarObservation.symbol == symbol)
            .group_by(
                MarketDailyBarObservation.source,
                MarketDailyBarObservation.trading_date,
            )
        )
        if sources is not None:
            max_ingested = max_ingested.where(
                MarketDailyBarObservation.source.in_(sources)
            )
        max_ingested = max_ingested.subquery()

        stmt = (
            select(MarketDailyBarObservation)
            .join(
                max_ingested,
                (
                    MarketDailyBarObservation.source == max_ingested.c.source
                )
                & (
                    MarketDailyBarObservation.trading_date == max_ingested.c.trading_date
                )
                & (
                    MarketDailyBarObservation.ingested_at == max_ingested.c.max_ingested_at
                ),
            )
            .where(MarketDailyBarObservation.symbol == symbol)
        )
        if sources is not None:
            stmt = stmt.where(MarketDailyBarObservation.source.in_(sources))
        stmt = stmt.order_by(MarketDailyBarObservation.trading_date.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


def _observation_from_bar(
    source: str,
    bar: DailyBar,
    *,
    observation_kind: str,
    supersedes_observation_id: int | None = None,
) -> MarketDailyBarObservation:
    return MarketDailyBarObservation(
        source=source,
        symbol=bar.symbol,
        trading_date=bar.trading_date,
        event_time=_session_close_placeholder(bar.trading_date),
        open=bar.open,
        high=bar.high,
        low=bar.low,
        close=bar.close,
        volume=bar.volume,
        raw_payload=bar.raw_payload,
        observation_kind=observation_kind,
        supersedes_observation_id=supersedes_observation_id,
    )


def _session_close_placeholder(trading_date: date) -> datetime:
    """Midnight UTC on ``trading_date``.

    A precise per-calendar session-close timestamp (which varies by exchange and by daylight
    saving time) is deferred; this column exists today primarily as the TimescaleDB hypertable
    partitioning key. Computing it precisely would require this repository to depend on
    ``aegis.domain.calendars``, which the persistence/domain module boundary does not require
    for Phase 1.
    """

    return datetime.combine(trading_date, time.min, tzinfo=UTC)
