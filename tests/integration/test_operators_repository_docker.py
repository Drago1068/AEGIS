"""Operators repository/migration integration test against the real Compose stack.

Scope (see `docs/architecture/decisions/0005-phase-4-operator-auth.md`): this test requires
`postgres` to already be up and healthy and the Alembic migrations applied
(`uv run --project backend alembic upgrade head`). Unlike the backend's own unit tests (which
use fakes and no real I/O), this test connects directly to the real database via the
backend's persistence layer to verify the migration and the repository's seed-once behavior
end to end. It does not go through the backend HTTP API.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from aegis.config.settings import get_settings
from aegis.domain.auth_passwords import verify_password
from aegis.persistence.database import create_engine, create_session_factory
from aegis.persistence.repositories.operators import OperatorRepository

_TEST_USERNAME = "aegis_operators_integration_test_user"
_TEST_PASSWORD = "aegis-operators-integration-test-password"


async def _delete_test_rows(session: AsyncSession) -> None:
    await session.execute(
        text("DELETE FROM operators WHERE username = :username"),
        {"username": _TEST_USERNAME},
    )
    await session.commit()


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    settings = get_settings()
    engine = create_engine(settings)
    factory = create_session_factory(engine)
    async with factory() as db_session:
        await _delete_test_rows(db_session)
        yield db_session
        await _delete_test_rows(db_session)
    await engine.dispose()


@pytest.mark.asyncio
async def test_migration_created_the_table_with_the_unique_constraint(
    session: AsyncSession,
) -> None:
    result = await session.execute(
        text("SELECT conname FROM pg_constraint WHERE conname = 'uq_operators_username'")
    )
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_ensure_seeded_inserts_once_and_hashes_password(session: AsyncSession) -> None:
    repository = OperatorRepository(session)
    total = (await session.execute(text("SELECT count(*) FROM operators"))).scalar_one()

    if total == 0:
        await repository.ensure_seeded(_TEST_USERNAME, _TEST_PASSWORD)
        operator = await repository.get_by_username(_TEST_USERNAME)
        assert operator is not None
        assert operator.username == _TEST_USERNAME
        assert operator.password_hash != _TEST_PASSWORD
        assert verify_password(_TEST_PASSWORD, operator.password_hash) is True

        await repository.ensure_seeded(_TEST_USERNAME, "must-not-replace")
        again = await repository.get_by_username(_TEST_USERNAME)
        assert again is not None
        assert again.password_hash == operator.password_hash
        assert verify_password("must-not-replace", again.password_hash) is False
    else:
        # Table already has operators from env bootstrap; seed-once must remain a no-op.
        before = (await session.execute(text("SELECT count(*) FROM operators"))).scalar_one()
        await repository.ensure_seeded(_TEST_USERNAME, _TEST_PASSWORD)
        after = (await session.execute(text("SELECT count(*) FROM operators"))).scalar_one()
        assert after == before
        assert await repository.get_by_username(_TEST_USERNAME) is None
