"""Create operators (Phase 4 single-role operator authentication).

Adds the operators table (ADR-0005): a mutable operational table storing the single
operator role's username and Argon2 password hash. Unlike
``market_daily_bar_observations``, this is a plain (non-hypertable) operational table - it
holds current authentication configuration, not a point-in-time observation.

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-28

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

_TABLE_NAME = "operators"
_UNIQUE_USERNAME_CONSTRAINT_NAME = "uq_operators_username"


def upgrade() -> None:
    op.create_table(
        _TABLE_NAME,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name="pk_operators"),
        sa.UniqueConstraint("username", name=_UNIQUE_USERNAME_CONSTRAINT_NAME),
    )


def downgrade() -> None:
    op.drop_table(_TABLE_NAME)
