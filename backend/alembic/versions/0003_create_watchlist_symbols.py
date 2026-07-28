"""Create watchlist_symbols (Phase 2 operational, database-backed ingestion watchlist).

Adds the operationally managed watchlist table (ADR-0003): a mutable, soft-deletable list of
symbols that on-demand and scheduled ingestion runs process. Unlike
``market_daily_bar_observations``, this is a plain (non-hypertable) operational table - it
holds current configuration state, not point-in-time observations.

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-28

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

_TABLE_NAME = "watchlist_symbols"
_UNIQUE_SYMBOL_CONSTRAINT_NAME = "uq_watchlist_symbols_symbol"


def upgrade() -> None:
    op.create_table(
        _TABLE_NAME,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_watchlist_symbols"),
        sa.UniqueConstraint("symbol", name=_UNIQUE_SYMBOL_CONSTRAINT_NAME),
    )


def downgrade() -> None:
    op.drop_table(_TABLE_NAME)
