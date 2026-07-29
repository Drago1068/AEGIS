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
    Float,
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
    place. Phase 12 (ADR-0013) allows multiple rows per ``(source, symbol, event_time)`` when a
    provider revises history: a ``correction`` row supersedes the prior current observation via
    ``supersedes_observation_id`` while preserving the initial row for audit. Reads use the
    latest ``ingested_at`` per ``(source, symbol, trading_date)``.

    ``id`` is paired with ``event_time`` in the primary key (rather than being a standalone
    primary key) because TimescaleDB requires every unique index on a hypertable, including
    the primary key, to include the partitioning column (``event_time``).
    """

    __tablename__ = "market_daily_bar_observations"
    __table_args__ = (
        PrimaryKeyConstraint("id", "event_time", name="pk_market_daily_bar_id_event_time"),
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
    observation_kind: Mapped[str] = mapped_column(String(32), nullable=False, default="initial")
    supersedes_observation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)


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


class Operator(Base):
    """A single-role operator account for Phase 4 session authentication.

    Mutable operational table (not an append-only observation): credentials may be updated in
    place. Bootstrap seeding from env happens only when the table is empty; see ADR-0005.
    """

    __tablename__ = "operators"
    __table_args__ = (UniqueConstraint("username", name="uq_operators_username"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class ResearchAssessmentSnapshot(Base):
    """An append-only research-only assessment snapshot (Phase 6, ADR-0007).

    Insert-only: never updated in place. ``state`` is always ``research_only`` in Phase 6;
    ``probability_confidence`` remains null (not calibrated). Not a Timescale hypertable.
    """

    __tablename__ = "research_assessment_snapshots"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    as_of_trading_date: Mapped[date] = mapped_column(Date, nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    method_id: Mapped[str] = mapped_column(String(64), nullable=False)
    method_version: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False)
    coverage_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    probability_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    components: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    input_source: Mapped[str] = mapped_column(String(64), nullable=False)
    lookback_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    lookback_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    bar_count: Mapped[int] = mapped_column(Integer, nullable=False)


class ResearchAssessmentOutcomeLabel(Base):
    """Append-only forward-return outcome label for a research assessment (Phase 13, ADR-0014).

    Evidence for a future calibration phase; not a probability or recommendation.
    """

    __tablename__ = "research_assessment_outcome_labels"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    assessment_snapshot_id: Mapped[int] = mapped_column(Integer, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    label_method_id: Mapped[str] = mapped_column(String(64), nullable=False)
    label_method_version: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False)
    as_of_trading_date: Mapped[date] = mapped_column(Date, nullable=False)
    labels: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    label_end_dates: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    bar_source: Mapped[str] = mapped_column(String(64), nullable=False)


class ResearchAssessmentProbabilityCalibration(Base):
    """Append-only probability calibration for a research assessment (Phase 15, ADR-0016).

    Research-only calibrated confidence from labeled historical corpus; not merged with
    coverage_confidence on the assessment row.
    """

    __tablename__ = "research_assessment_probability_calibrations"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    assessment_snapshot_id: Mapped[int] = mapped_column(Integer, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    calibration_method_id: Mapped[str] = mapped_column(String(64), nullable=False)
    calibration_method_version: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False)
    probability_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    corpus_count: Mapped[int] = mapped_column(Integer, nullable=False)
    bucket_count: Mapped[int] = mapped_column(Integer, nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
