"""Create research_assessment_probability_calibrations (Phase 15, ADR-0016).

Append-only probability calibration rows linked to assessment snapshots. Research-only;
distinct from coverage_confidence.

Revision ID: 0008
Revises: 0007
Create Date: 2026-07-29

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

_TABLE_NAME = "research_assessment_probability_calibrations"


def upgrade() -> None:
    op.create_table(
        _TABLE_NAME,
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("assessment_snapshot_id", sa.Integer(), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("calibration_method_id", sa.String(length=64), nullable=False),
        sa.Column("calibration_method_version", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("probability_confidence", sa.Float(), nullable=False),
        sa.Column("corpus_count", sa.Integer(), nullable=False),
        sa.Column("bucket_count", sa.Integer(), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_research_probability_calibrations"),
        sa.ForeignKeyConstraint(
            ["assessment_snapshot_id"],
            ["research_assessment_snapshots.id"],
            name="fk_probability_calibrations_assessment_snapshot_id",
        ),
    )
    op.create_index(
        "ix_probability_calibrations_assessment_computed_at",
        _TABLE_NAME,
        ["assessment_snapshot_id", "computed_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_probability_calibrations_assessment_computed_at",
        table_name=_TABLE_NAME,
    )
    op.drop_table(_TABLE_NAME)
