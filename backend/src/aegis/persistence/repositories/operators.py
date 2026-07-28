"""Repository for the operators table (Phase 4 authentication identity store).

Distinct from append-only observation stores: ``operators`` is a mutable operational table.
Bootstrap seeding from environment credentials runs only when the table is completely empty;
see ``docs/architecture/decisions/0005-phase-4-operator-auth.md``.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from aegis.domain.auth_passwords import hash_password
from aegis.persistence.models import Operator


class OperatorRepository:
    """SQLAlchemy-backed storage for operator accounts."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_username(self, username: str) -> Operator | None:
        """Return the operator row for ``username``, or ``None`` if not found."""

        result = await self._session.execute(
            select(Operator)
            .where(Operator.username == username)
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    async def ensure_seeded(self, username: str, password: str) -> None:
        """Insert the bootstrap operator only if the table is currently completely empty.

        Hashes ``password`` with Argon2 before insert. After any row exists (seeded or
        otherwise), this is a permanent no-op and environment credentials are not re-applied.
        See ADR-0005.
        """

        total = (
            await self._session.execute(select(func.count()).select_from(Operator))
        ).scalar_one()
        if total > 0:
            return

        operator = Operator(username=username, password_hash=hash_password(password))
        self._session.add(operator)
        await self._session.commit()
