"""Infrastructure baseline: enable and verify the TimescaleDB extension.

This migration enables the TimescaleDB extension on the target PostgreSQL database and
verifies it is present. It creates no market-data, trading, or other domain tables; those
are added by later, phase-gated migrations once their domain models exist.

Revision ID: 0001
Revises:
Create Date: 2026-07-27

"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
from sqlalchemy import text

revision: str = "0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")

    connection = op.get_bind()
    installed = connection.execute(
        text("SELECT extname FROM pg_extension WHERE extname = 'timescaledb'")
    ).scalar_one_or_none()
    if installed is None:
        raise RuntimeError(
            "TimescaleDB extension was not found installed after CREATE EXTENSION; "
            "check that the target PostgreSQL image bundles TimescaleDB."
        )


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS timescaledb;")
