"""Market data repository/migration integration test against the real Compose stack.

Scope (see `docs/architecture/decisions/0002-phase-1-market-data-ingestion.md`): this test
requires `postgres` to already be up and healthy (`docker compose up -d postgres`, or the full
stack) and the Alembic migrations applied (`uv run --project backend alembic upgrade head`).
Unlike the backend's own unit tests (which use fakes and no real I/O), this test connects
directly to the real database via the backend's persistence layer to verify the migration,
the hypertable, and the repository's idempotent insert/read behavior end to end. It does not
go through the backend HTTP API.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import date
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from aegis.config.settings import get_settings
from aegis.persistence.database import create_engine, create_session_factory
from aegis.persistence.repositories.market_data import MarketDailyBarRepository
from aegis.providers.market_data import DailyBar

_TEST_SOURCE = "integration_test"
_TEST_SYMBOL = "AEGIS_INTEGRATION_TEST"


def _bar(trading_date: date) -> DailyBar:
    return DailyBar(
        symbol=_TEST_SYMBOL,
        trading_date=trading_date,
        open=Decimal("100.00"),
        high=Decimal("101.00"),
        low=Decimal("99.00"),
        close=Decimal("100.50"),
        volume=123456,
        raw_payload={"note": "written by test_market_data_repository_docker.py"},
    )


async def _delete_test_rows(session: AsyncSession) -> None:
    await session.execute(
        text(
            "DELETE FROM market_daily_bar_observations "
            "WHERE source = :source AND symbol = :symbol"
        ),
        {"source": _TEST_SOURCE, "symbol": _TEST_SYMBOL},
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
async def test_migration_created_a_hypertable_with_the_unique_constraint(
    session: AsyncSession,
) -> None:
    hypertable_result = await session.execute(
        text(
            "SELECT hypertable_name FROM timescaledb_information.hypertables "
            "WHERE hypertable_name = 'market_daily_bar_observations'"
        )
    )
    assert hypertable_result.scalar_one_or_none() == "market_daily_bar_observations"

    constraint_result = await session.execute(
        text(
            "SELECT conname FROM pg_constraint "
            "WHERE conname = 'uq_market_daily_bar_source_symbol_event_time'"
        )
    )
    assert constraint_result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_insert_idempotent_reinsert_and_read_round_trip(session: AsyncSession) -> None:
    repository = MarketDailyBarRepository(session)
    bars = [_bar(date(2024, 1, 2)), _bar(date(2024, 1, 3))]

    first_run_inserted = await repository.save_many(_TEST_SOURCE, bars)
    assert first_run_inserted == 2

    second_run_inserted = await repository.save_many(_TEST_SOURCE, bars)
    assert second_run_inserted == 0

    existing_dates = await repository.existing_trading_dates(_TEST_SOURCE, _TEST_SYMBOL)
    assert existing_dates == {date(2024, 1, 2), date(2024, 1, 3)}

    recent = await repository.list_recent(_TEST_SYMBOL, limit=10)
    assert [row.trading_date for row in recent] == [date(2024, 1, 3), date(2024, 1, 2)]
    assert recent[0].source == _TEST_SOURCE
    assert recent[0].open == Decimal("100.00")
    assert recent[0].volume == 123456
