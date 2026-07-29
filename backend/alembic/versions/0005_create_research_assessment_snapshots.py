"""Create research_assessment_snapshots (Phase 6 research-only assessments).

Adds the append-only research assessment table (ADR-0007): plain Postgres (not a
Timescale hypertable). Rows are insert-only evidence snapshots with research-only state,
coverage confidence, null probability confidence, component JSON, and input provenance.

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-28

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

_TABLE_NAME = "research_assessment_snapshots"


def upgrade() -> None:
    op.create_table(
        _TABLE_NAME,
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("as_of_trading_date", sa.Date(), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("method_id", sa.String(length=64), nullable=False),
        sa.Column("method_version", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("coverage_confidence", sa.Float(), nullable=False),
        sa.Column("probability_confidence", sa.Float(), nullable=True),
        sa.Column(
            "components",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("schema_version", sa.Integer(), nullable=False),
        sa.Column("input_source", sa.String(length=64), nullable=False),
        sa.Column("lookback_start_date", sa.Date(), nullable=False),
        sa.Column("lookback_end_date", sa.Date(), nullable=False),
        sa.Column("bar_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_research_assessment_snapshots"),
    )
    op.create_index(
        "ix_research_assessment_snapshots_symbol_computed_at",
        _TABLE_NAME,
        ["symbol", "computed_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_research_assessment_snapshots_symbol_computed_at",
        table_name=_TABLE_NAME,
    )
    op.drop_table(_TABLE_NAME)
