"""Create market_daily_bar_observations and convert it to a TimescaleDB hypertable.

Adds the first domain data table (Phase 1, per ADR-0002): validated daily OHLCV observations,
append-only, with a unique constraint that makes re-ingesting an already-stored day a no-op
rather than a duplicate row. Partitioned on ``event_time`` via ``create_hypertable``.

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-27

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

_TABLE_NAME = "market_daily_bar_observations"
_UNIQUE_CONSTRAINT_NAME = "uq_market_daily_bar_source_symbol_event_time"
_SYMBOL_DATE_INDEX_NAME = "ix_market_daily_bar_symbol_trading_date"


def upgrade() -> None:
    op.create_table(
        _TABLE_NAME,
        # `id` is paired with `event_time` in the primary key (not a standalone primary key)
        # because TimescaleDB requires every unique index on a hypertable, including the
        # primary key, to include the partitioning column.
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("trading_date", sa.Date(), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("open", sa.Numeric(18, 6), nullable=False),
        sa.Column("high", sa.Numeric(18, 6), nullable=False),
        sa.Column("low", sa.Numeric(18, 6), nullable=False),
        sa.Column("close", sa.Numeric(18, 6), nullable=False),
        sa.Column("volume", sa.BigInteger(), nullable=False),
        sa.Column(
            "data_quality", sa.String(length=32), nullable=False, server_default="primary"
        ),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("raw_payload", JSONB(), nullable=False),
        sa.PrimaryKeyConstraint("id", "event_time", name="pk_market_daily_bar_id_event_time"),
        sa.UniqueConstraint(
            "source", "symbol", "event_time", name=_UNIQUE_CONSTRAINT_NAME
        ),
    )
    op.create_index(
        _SYMBOL_DATE_INDEX_NAME, _TABLE_NAME, ["symbol", "trading_date"], unique=False
    )

    # migrate_data is unnecessary (the table is freshly created and empty); chunk_time_interval
    # defaults to 7 days, appropriate for low-volume daily-bar data.
    op.execute(f"SELECT create_hypertable('{_TABLE_NAME}', 'event_time');")


def downgrade() -> None:
    op.drop_index(_SYMBOL_DATE_INDEX_NAME, table_name=_TABLE_NAME)
    op.drop_table(_TABLE_NAME)
