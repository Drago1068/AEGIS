"""Add outcome_horizon_key to probability calibrations (Phase 41, ADR-0042).

Revision ID: 0009
Revises: 0008
Create Date: 2026-07-30

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

_TABLE_NAME = "research_assessment_probability_calibrations"


def upgrade() -> None:
    op.add_column(
        _TABLE_NAME,
        sa.Column(
            "outcome_horizon_key",
            sa.String(length=64),
            nullable=False,
            server_default="forward_return_5",
        ),
    )
    op.create_index(
        "ix_probability_calibrations_assessment_horizon_computed",
        _TABLE_NAME,
        ["assessment_snapshot_id", "outcome_horizon_key", "computed_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_probability_calibrations_assessment_horizon_computed",
        table_name=_TABLE_NAME,
    )
    op.drop_column(_TABLE_NAME, "outcome_horizon_key")
