"""Watchlist repository/migration integration test against the real Compose stack.

Scope (see `docs/architecture/decisions/0003-phase-2-scheduled-watchlist.md`): this test
requires `postgres` to already be up and healthy and the Alembic migrations applied
(`uv run --project backend alembic upgrade head`). Unlike the backend's own unit tests (which
use fakes and no real I/O), this test connects directly to the real database via the
backend's persistence layer to verify the migration and the repository's seed/add/deactivate
behavior end to end. It does not go through the backend HTTP API.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from aegis.config.settings import get_settings
from aegis.persistence.database import create_engine, create_session_factory
from aegis.persistence.repositories.watchlist import WatchlistRepository

_TEST_SYMBOLS = ("AEGIS_WATCHLIST_TEST_A", "AEGIS_WATCHLIST_TEST_B")


async def _delete_test_rows(session: AsyncSession) -> None:
    await session.execute(
        text("DELETE FROM watchlist_symbols WHERE symbol = ANY(:symbols)"),
        {"symbols": list(_TEST_SYMBOLS)},
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
        text(
            "SELECT conname FROM pg_constraint WHERE conname = 'uq_watchlist_symbols_symbol'"
        )
    )
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_add_deactivate_and_reactivate_round_trip(session: AsyncSession) -> None:
    repository = WatchlistRepository(session)
    symbol_a, symbol_b = _TEST_SYMBOLS

    added = await repository.add(symbol_a)
    assert added.symbol == symbol_a
    assert added.is_active is True

    active = await repository.list_active()
    assert symbol_a in active

    removed = await repository.deactivate(symbol_a)
    assert removed is True
    assert symbol_a not in await repository.list_active()

    removed_again = await repository.deactivate(symbol_a)
    assert removed_again is False

    reactivated = await repository.add(symbol_a)
    assert reactivated.is_active is True
    assert symbol_a in await repository.list_active()

    await repository.add(symbol_b)
    assert set(await repository.list_active()) >= {symbol_a, symbol_b}


@pytest.mark.asyncio
async def test_ensure_seeded_is_a_noop_once_any_row_exists(session: AsyncSession) -> None:
    repository = WatchlistRepository(session)
    symbol_a, symbol_b = _TEST_SYMBOLS

    await repository.add(symbol_a)
    await repository.deactivate(symbol_a)

    # The table is non-empty (one inactive row), so seeding must not insert symbol_b.
    await repository.ensure_seeded([symbol_b])

    assert symbol_b not in await repository.list_active()
