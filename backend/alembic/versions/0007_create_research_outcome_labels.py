"""Create research_assessment_outcome_labels (Phase 13, ADR-0014).

Append-only forward-return outcome labels linked to assessment snapshots for calibration
evidence prep. Not probabilities or recommendations.

Revision ID: 0007
Revises: 0006
Create Date: 2026-07-29

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

_TABLE_NAME = "research_assessment_outcome_labels"


def upgrade() -> None:
    op.create_table(
        _TABLE_NAME,
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("assessment_snapshot_id", sa.Integer(), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("label_method_id", sa.String(length=64), nullable=False),
        sa.Column("label_method_version", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("as_of_trading_date", sa.Date(), nullable=False),
        sa.Column(
            "labels",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "label_end_dates",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("schema_version", sa.Integer(), nullable=False),
        sa.Column("bar_source", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_research_assessment_outcome_labels"),
        sa.ForeignKeyConstraint(
            ["assessment_snapshot_id"],
            ["research_assessment_snapshots.id"],
            name="fk_outcome_labels_assessment_snapshot_id",
        ),
    )
    op.create_index(
        "ix_outcome_labels_assessment_computed_at",
        _TABLE_NAME,
        ["assessment_snapshot_id", "computed_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_outcome_labels_assessment_computed_at",
        table_name=_TABLE_NAME,
    )
    op.drop_table(_TABLE_NAME)
