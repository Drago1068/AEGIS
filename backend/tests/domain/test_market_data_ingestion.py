"""Unit tests for MarketDataIngestionService orchestration, using fake doubles (no real I/O)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from aegis.domain.market_data_ingestion import MarketDataIngestionService
from aegis.domain.market_data_validation import RejectionReason
from aegis.providers.errors import ProviderError
from aegis.providers.market_data import DailyBar

_CALENDAR = "NYSE"
_SOURCE = "alpha_vantage"
# A normal NYSE trading day, used as both a bar date and the "as_of" run date.
_AS_OF = date(2024, 1, 2)


def _bar(symbol: str, trading_date: date, **overrides: object) -> DailyBar:
    defaults: dict[str, object] = {
        "symbol": symbol,
        "trading_date": trading_date,
        "open": Decimal("100"),
        "high": Decimal("110"),
        "low": Decimal("90"),
        "close": Decimal("105"),
        "volume": 1000,
        "raw_payload": {},
    }
    defaults.update(overrides)
    return DailyBar(**defaults)  # type: ignore[arg-type]


class FakeProvider:
    def __init__(self, bars_by_symbol: dict[str, list[DailyBar]]) -> None:
        self._bars_by_symbol = bars_by_symbol
        self.requested_symbols: list[str] = []

    async def fetch_daily_bars(self, symbol: str) -> list[DailyBar]:
        self.requested_symbols.append(symbol)
        if symbol not in self._bars_by_symbol:
            raise ProviderError(f"no fixture bars for {symbol!r}")
        return self._bars_by_symbol[symbol]


class FakeRepository:
    def __init__(self, existing: dict[str, set[date]] | None = None) -> None:
        self._existing: dict[str, set[date]] = existing or {}
        self.saved_bars: list[DailyBar] = []

    async def existing_trading_dates(self, source: str, symbol: str) -> set[date]:
        return self._existing.get(symbol, set())

    async def save_many(self, source: str, bars: list[DailyBar]) -> int:
        self.saved_bars.extend(bars)
        return len(bars)


def _service(
    provider: FakeProvider, repository: FakeRepository, *, as_of: date = _AS_OF
) -> MarketDataIngestionService:
    return MarketDataIngestionService(
        provider,
        repository,
        source=_SOURCE,
        calendar_name=_CALENDAR,
        max_latest_bar_staleness_trading_days=3,
        as_of=as_of,
    )


@pytest.mark.asyncio
async def test_valid_bars_are_stored() -> None:
    bars = [_bar("AAPL", _AS_OF)]
    provider = FakeProvider({"AAPL": bars})
    repository = FakeRepository()

    run_result = await _service(provider, repository).run(["AAPL"])

    assert len(run_result.results) == 1
    result = run_result.results[0]
    assert result.symbol == "AAPL"
    assert result.stored_count == 1
    assert result.rejected_count == 0
    assert result.error is None
    assert repository.saved_bars == bars


@pytest.mark.asyncio
async def test_invalid_bars_are_rejected_and_counted_not_stored() -> None:
    bad_bar = _bar("AAPL", _AS_OF, open=Decimal("-1"))
    provider = FakeProvider({"AAPL": [bad_bar]})
    repository = FakeRepository()

    run_result = await _service(provider, repository).run(["AAPL"])

    result = run_result.results[0]
    assert result.stored_count == 0
    assert result.rejected_count == 1
    assert result.rejections == {RejectionReason.NON_POSITIVE: 1}
    assert repository.saved_bars == []


@pytest.mark.asyncio
async def test_already_stored_dates_are_skipped_idempotently() -> None:
    bars = [_bar("AAPL", date(2023, 12, 29)), _bar("AAPL", _AS_OF)]
    provider = FakeProvider({"AAPL": bars})
    repository = FakeRepository(existing={"AAPL": {date(2023, 12, 29)}})

    run_result = await _service(provider, repository).run(["AAPL"])

    result = run_result.results[0]
    assert result.skipped_existing_count == 1
    assert result.stored_count == 1
    assert [bar.trading_date for bar in repository.saved_bars] == [_AS_OF]


@pytest.mark.asyncio
async def test_one_symbol_provider_failure_does_not_abort_the_run() -> None:
    good_bars = [_bar("MSFT", _AS_OF)]
    provider = FakeProvider({"MSFT": good_bars})
    repository = FakeRepository()

    run_result = await _service(provider, repository).run(["BADSYMBOL", "MSFT"])

    assert provider.requested_symbols == ["BADSYMBOL", "MSFT"]
    bad_result, good_result = run_result.results
    assert bad_result.symbol == "BADSYMBOL"
    assert bad_result.error is not None
    assert bad_result.stored_count == 0
    assert good_result.symbol == "MSFT"
    assert good_result.stored_count == 1
    assert good_result.error is None


@pytest.mark.asyncio
async def test_empty_provider_response_stores_nothing() -> None:
    provider = FakeProvider({"AAPL": []})
    repository = FakeRepository()

    run_result = await _service(provider, repository).run(["AAPL"])

    result = run_result.results[0]
    assert result.stored_count == 0
    assert result.rejected_count == 0
    assert result.skipped_existing_count == 0
    assert repository.saved_bars == []


@pytest.mark.asyncio
async def test_stale_latest_bar_is_rejected_but_older_bars_in_same_run_are_not() -> None:
    stale_latest = _bar("AAPL", date(2023, 12, 1))
    provider = FakeProvider({"AAPL": [stale_latest]})
    repository = FakeRepository()

    run_result = await _service(provider, repository).run(["AAPL"])

    result = run_result.results[0]
    assert result.rejections == {RejectionReason.STALE: 1}
    assert result.stored_count == 0
