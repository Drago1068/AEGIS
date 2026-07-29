"""Allow append-only provider corrections on market_daily_bar_observations.

Phase 12 (ADR-0013): drop the unique constraint on (source, symbol, event_time), add
observation_kind and supersedes_observation_id, and index for current-bar reads.

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-29

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

_TABLE_NAME = "market_daily_bar_observations"
_UNIQUE_CONSTRAINT_NAME = "uq_market_daily_bar_source_symbol_event_time"
_CURRENT_BAR_INDEX_NAME = "ix_market_daily_bar_source_symbol_date_ingested"


def upgrade() -> None:
    op.drop_constraint(_UNIQUE_CONSTRAINT_NAME, _TABLE_NAME, type_="unique")
    op.add_column(
        _TABLE_NAME,
        sa.Column(
            "observation_kind",
            sa.String(length=32),
            nullable=False,
            server_default="initial",
        ),
    )
    op.add_column(
        _TABLE_NAME,
        sa.Column("supersedes_observation_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        _CURRENT_BAR_INDEX_NAME,
        _TABLE_NAME,
        ["source", "symbol", "trading_date", "ingested_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(_CURRENT_BAR_INDEX_NAME, table_name=_TABLE_NAME)
    op.drop_column(_TABLE_NAME, "supersedes_observation_id")
    op.drop_column(_TABLE_NAME, "observation_kind")
    op.create_unique_constraint(
        _UNIQUE_CONSTRAINT_NAME,
        _TABLE_NAME,
        ["source", "symbol", "event_time"],
    )
