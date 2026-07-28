"""SQLAlchemy declarative models.

This module defines only the ORM mapping (schema shape); domain validation and business rules
live in :mod:`aegis.domain`, never here, per the persistence/domain module boundary.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Identity,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Shared declarative base for all AEGIS ORM models."""


class MarketDailyBarObservation(Base):
    """A single validated, stored daily OHLCV observation.

    Append-only per ``docs/architecture/data-model.md``: rows are inserted, never updated in
    place. The unique constraint on ``(source, symbol, event_time)`` makes re-ingestion of an
    already-stored day a no-op (``ON CONFLICT DO NOTHING`` in the repository), not a
    correction; see ADR-0002 for why this is distinct from a provider-revision correction.
    ``event_time`` (rather than ``trading_date``) is in the constraint because TimescaleDB
    requires every unique constraint on a hypertable to include its partitioning column;
    ``event_time`` is derived deterministically (1:1) from ``trading_date``, so this is
    equivalent for our purposes.

    ``id`` is paired with ``event_time`` in the primary key (rather than being a standalone
    primary key) because TimescaleDB requires every unique index on a hypertable, including
    the primary key, to include the partitioning column (``event_time``).
    """

    __tablename__ = "market_daily_bar_observations"
    __table_args__ = (
        PrimaryKeyConstraint("id", "event_time", name="pk_market_daily_bar_id_event_time"),
        UniqueConstraint(
            "source", "symbol", "event_time", name="uq_market_daily_bar_source_symbol_event_time"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    trading_date: Mapped[date] = mapped_column(Date, nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    open: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    data_quality: Mapped[str] = mapped_column(String(32), nullable=False, default="primary")
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    raw_payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)


class WatchlistSymbol(Base):
    """An operationally managed symbol that ingestion (on-demand or scheduled) processes.

    Unlike :class:`MarketDailyBarObservation`, this is a mutable operational table, not an
    append-only observation: a removed symbol is soft-deactivated (``is_active=False``), never
    hard-deleted, and re-adding it reactivates the existing row. See ADR-0003 for why the
    append-only, point-in-time conventions in ``docs/architecture/data-model.md`` intentionally
    do not apply to this table (it is current configuration, not a market observation).
    """

    __tablename__ = "watchlist_symbols"
    __table_args__ = (UniqueConstraint("symbol", name="uq_watchlist_symbols_symbol"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
