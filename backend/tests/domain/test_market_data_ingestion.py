"""Unit tests for MarketDataIngestionService orchestration, using fake doubles (no real I/O)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from aegis.domain.market_data_corrections import StoredBarSnapshot
from aegis.domain.market_data_ingestion import MarketDataIngestionService
from aegis.domain.market_data_validation import RejectionReason
from aegis.providers.errors import (
    ProviderError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)
from aegis.providers.market_data import DailyBar

_CALENDAR = "NYSE"
_SOURCE = "alpha_vantage"
_SECONDARY_SOURCE = "polygon"
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


def _snapshot(
    trading_date: date,
    *,
    observation_id: int = 1,
    close: Decimal = Decimal("105"),
    volume: int = 1000,
) -> StoredBarSnapshot:
    return StoredBarSnapshot(
        id=observation_id,
        trading_date=trading_date,
        open=Decimal("100"),
        high=Decimal("110"),
        low=Decimal("90"),
        close=close,
        volume=volume,
        data_quality="primary",
    )


class FakeProvider:
    def __init__(
        self,
        bars_by_symbol: dict[str, list[DailyBar]] | None = None,
        *,
        errors_by_symbol: dict[str, Exception] | None = None,
    ) -> None:
        self._bars_by_symbol = bars_by_symbol or {}
        self._errors_by_symbol = errors_by_symbol or {}
        self.requested_symbols: list[str] = []

    async def fetch_daily_bars(self, symbol: str) -> list[DailyBar]:
        self.requested_symbols.append(symbol)
        if symbol in self._errors_by_symbol:
            raise self._errors_by_symbol[symbol]
        if symbol not in self._bars_by_symbol:
            raise ProviderError(f"no fixture bars for {symbol!r}")
        return self._bars_by_symbol[symbol]


class FakeRepository:
    def __init__(
        self,
        current: dict[tuple[str, str], dict[date, StoredBarSnapshot]] | None = None,
        *,
        max_trading_dates: dict[tuple[str, str], date] | None = None,
    ) -> None:
        self._current = current or {}
        self._max_trading_dates = max_trading_dates or {}
        self.saved: list[tuple[str, DailyBar]] = []
        self.corrections: list[tuple[str, DailyBar, int]] = []

    async def get_current_by_trading_dates(
        self,
        source: str,
        symbol: str,
        trading_dates: set[date],
    ) -> dict[date, StoredBarSnapshot]:
        stored = self._current.get((source, symbol), {})
        return {d: stored[d] for d in trading_dates if d in stored}

    async def get_max_trading_date(self, source: str, symbol: str) -> date | None:
        if (source, symbol) in self._max_trading_dates:
            return self._max_trading_dates[(source, symbol)]
        stored = self._current.get((source, symbol), {})
        if not stored:
            return None
        return max(stored)

    async def save_many(self, source: str, bars: list[DailyBar]) -> int:
        self.saved.extend((source, bar) for bar in bars)
        return len(bars)

    async def save_corrections(
        self,
        source: str,
        corrections: list[tuple[DailyBar, int]],
    ) -> int:
        for bar, supersedes_id in corrections:
            self.corrections.append((source, bar, supersedes_id))
        return len(corrections)

    @property
    def saved_bars(self) -> list[DailyBar]:
        return [bar for _, bar in self.saved]


def _service(
    provider: FakeProvider,
    repository: FakeRepository,
    *,
    as_of: date = _AS_OF,
    source: str = _SOURCE,
    secondary_provider: FakeProvider | None = None,
    secondary_source: str | None = None,
) -> MarketDataIngestionService:
    return MarketDataIngestionService(
        provider,
        repository,
        source=source,
        calendar_name=_CALENDAR,
        max_latest_bar_staleness_trading_days=3,
        as_of=as_of,
        secondary_provider=secondary_provider,
        secondary_source=secondary_source,
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
    assert result.corrected_count == 0
    assert result.rejected_count == 0
    assert result.error is None
    assert result.latest_trading_date == _AS_OF
    assert result.latest_trading_date_source == _SOURCE
    assert result.primary_latest_trading_date == _AS_OF
    assert repository.saved_bars == bars


@pytest.mark.asyncio
async def test_invalid_bars_are_rejected_and_counted_not_stored() -> None:
    bad_bar = _bar("AAPL", _AS_OF, open=Decimal("-1"))
    provider = FakeProvider({"AAPL": [bad_bar]})
    repository = FakeRepository()

    run_result = await _service(provider, repository).run(["AAPL"])

    result = run_result.results[0]
    assert result.stored_count == 0
    assert result.corrected_count == 0
    assert result.rejected_count == 1
    assert result.rejections == {RejectionReason.NON_POSITIVE: 1}
    assert repository.saved_bars == []


@pytest.mark.asyncio
async def test_already_stored_dates_are_skipped_idempotently() -> None:
    bars = [_bar("AAPL", date(2023, 12, 29)), _bar("AAPL", _AS_OF)]
    provider = FakeProvider({"AAPL": bars})
    repository = FakeRepository(
        current={
            (_SOURCE, "AAPL"): {
                date(2023, 12, 29): _snapshot(date(2023, 12, 29), observation_id=10),
            }
        }
    )

    run_result = await _service(provider, repository).run(["AAPL"])

    result = run_result.results[0]
    assert result.skipped_existing_count == 1
    assert result.stored_count == 1
    assert result.corrected_count == 0
    assert result.latest_trading_date == _AS_OF
    assert [bar.trading_date for bar in repository.saved_bars] == [_AS_OF]


@pytest.mark.asyncio
async def test_latest_trading_date_null_when_provider_errors() -> None:
    provider = FakeProvider(errors_by_symbol={"AAPL": ProviderError("down")})
    repository = FakeRepository()

    run_result = await _service(provider, repository).run(["AAPL"])

    result = run_result.results[0]
    assert result.error is not None
    assert result.latest_trading_date is None
    assert result.primary_latest_trading_date is None


@pytest.mark.asyncio
async def test_material_revision_inserts_correction_row() -> None:
    revised = _bar("AAPL", _AS_OF, close=Decimal("110"))
    provider = FakeProvider({"AAPL": [revised]})
    repository = FakeRepository(
        current={
            (_SOURCE, "AAPL"): {
                _AS_OF: _snapshot(_AS_OF, observation_id=42, close=Decimal("105")),
            }
        }
    )

    run_result = await _service(provider, repository).run(["AAPL"])

    result = run_result.results[0]
    assert result.stored_count == 0
    assert result.corrected_count == 1
    assert result.skipped_existing_count == 0
    assert repository.corrections == [(_SOURCE, revised, 42)]


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
    assert result.corrected_count == 0
    assert result.rejected_count == 0
    assert result.skipped_existing_count == 0
    assert result.latest_trading_date is None
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
    assert result.latest_trading_date == date(2023, 12, 1)


@pytest.mark.asyncio
async def test_primary_success_also_refreshes_secondary_tip() -> None:
    primary_bars = [_bar("AAPL", _AS_OF)]
    secondary_tip = date(2024, 1, 3)
    secondary_bars = [
        _bar(
            "AAPL",
            secondary_tip,
            open=Decimal("990"),
            high=Decimal("1000"),
            low=Decimal("980"),
            close=Decimal("999"),
        )
    ]
    primary = FakeProvider({"AAPL": primary_bars})
    secondary = FakeProvider({"AAPL": secondary_bars})
    repository = FakeRepository()

    run_result = await _service(
        primary,
        repository,
        secondary_provider=secondary,
        secondary_source=_SECONDARY_SOURCE,
        as_of=secondary_tip,
    ).run(["AAPL"])

    result = run_result.results[0]
    assert secondary.requested_symbols == ["AAPL"]
    assert result.stored_count == 2
    assert result.latest_trading_date == secondary_tip
    assert result.latest_trading_date_source == _SECONDARY_SOURCE
    assert result.primary_latest_trading_date == _AS_OF
    assert repository.saved == [
        (_SOURCE, primary_bars[0]),
        (_SECONDARY_SOURCE, secondary_bars[0]),
    ]


@pytest.mark.asyncio
async def test_rate_limit_on_primary_still_refreshes_secondary() -> None:
    secondary_bars = [_bar("AAPL", _AS_OF)]
    primary = FakeProvider(
        errors_by_symbol={"AAPL": ProviderRateLimitError("rate limited")}
    )
    secondary = FakeProvider({"AAPL": secondary_bars})
    repository = FakeRepository()

    run_result = await _service(
        primary,
        repository,
        secondary_provider=secondary,
        secondary_source=_SECONDARY_SOURCE,
    ).run(["AAPL"])

    assert primary.requested_symbols == ["AAPL"]
    assert secondary.requested_symbols == ["AAPL"]
    assert run_result.results[0].error is None
    assert run_result.results[0].stored_count == 1
    assert run_result.results[0].latest_trading_date_source == _SECONDARY_SOURCE
    assert run_result.results[0].primary_latest_trading_date is None
    assert repository.saved == [(_SECONDARY_SOURCE, secondary_bars[0])]


@pytest.mark.asyncio
async def test_primary_fetch_error_falls_back_to_stored_primary_tip() -> None:
    stored_tip = date(2024, 1, 2)
    secondary_tip = date(2024, 1, 3)
    secondary_bars = [
        _bar(
            "AAPL",
            secondary_tip,
            open=Decimal("990"),
            high=Decimal("1000"),
            low=Decimal("980"),
            close=Decimal("999"),
        )
    ]
    primary = FakeProvider(
        errors_by_symbol={"AAPL": ProviderRateLimitError("rate limited")}
    )
    secondary = FakeProvider({"AAPL": secondary_bars})
    repository = FakeRepository(
        max_trading_dates={(_SOURCE, "AAPL"): stored_tip},
    )

    run_result = await _service(
        primary,
        repository,
        secondary_provider=secondary,
        secondary_source=_SECONDARY_SOURCE,
        as_of=secondary_tip,
    ).run(["AAPL"])

    result = run_result.results[0]
    assert result.error is None
    assert result.latest_trading_date == secondary_tip
    assert result.latest_trading_date_source == _SECONDARY_SOURCE
    assert result.primary_latest_trading_date == stored_tip


@pytest.mark.asyncio
async def test_primary_empty_fetch_falls_back_to_stored_primary_tip() -> None:
    stored_tip = date(2023, 12, 29)
    primary = FakeProvider({"AAPL": []})
    repository = FakeRepository(
        max_trading_dates={(_SOURCE, "AAPL"): stored_tip},
    )

    run_result = await _service(primary, repository).run(["AAPL"])

    result = run_result.results[0]
    assert result.error is None
    assert result.latest_trading_date is None
    assert result.primary_latest_trading_date == stored_tip


@pytest.mark.asyncio
async def test_primary_only_error_falls_back_to_stored_primary_tip() -> None:
    stored_tip = date(2024, 1, 2)
    primary = FakeProvider(errors_by_symbol={"AAPL": ProviderError("down")})
    repository = FakeRepository(
        max_trading_dates={(_SOURCE, "AAPL"): stored_tip},
    )

    run_result = await _service(primary, repository).run(["AAPL"])

    result = run_result.results[0]
    assert result.error is not None
    assert result.latest_trading_date is None
    assert result.primary_latest_trading_date == stored_tip


@pytest.mark.asyncio
async def test_unavailable_on_primary_still_refreshes_secondary() -> None:
    secondary_bars = [_bar("AAPL", _AS_OF)]
    primary = FakeProvider(
        errors_by_symbol={"AAPL": ProviderUnavailableError("transport down")}
    )
    secondary = FakeProvider({"AAPL": secondary_bars})
    repository = FakeRepository()

    run_result = await _service(
        primary,
        repository,
        secondary_provider=secondary,
        secondary_source=_SECONDARY_SOURCE,
    ).run(["AAPL"])

    assert repository.saved == [(_SECONDARY_SOURCE, secondary_bars[0])]
    assert run_result.results[0].stored_count == 1


@pytest.mark.asyncio
async def test_hard_primary_error_still_allows_secondary_tip_catch_up() -> None:
    secondary_bars = [_bar("AAPL", _AS_OF)]
    primary = FakeProvider(
        errors_by_symbol={"AAPL": ProviderError("invalid symbol")}
    )
    secondary = FakeProvider({"AAPL": secondary_bars})
    repository = FakeRepository()

    run_result = await _service(
        primary,
        repository,
        secondary_provider=secondary,
        secondary_source=_SECONDARY_SOURCE,
    ).run(["AAPL"])

    assert secondary.requested_symbols == ["AAPL"]
    assert run_result.results[0].error is None
    assert run_result.results[0].stored_count == 1
    assert repository.saved == [(_SECONDARY_SOURCE, secondary_bars[0])]


@pytest.mark.asyncio
async def test_both_providers_fail_records_combined_error() -> None:
    primary = FakeProvider(
        errors_by_symbol={"AAPL": ProviderRateLimitError("primary limited")}
    )
    secondary = FakeProvider(
        errors_by_symbol={"AAPL": ProviderUnavailableError("secondary down")}
    )
    repository = FakeRepository()

    run_result = await _service(
        primary,
        repository,
        secondary_provider=secondary,
        secondary_source=_SECONDARY_SOURCE,
    ).run(["AAPL"])

    error = run_result.results[0].error
    assert error is not None
    assert "primary limited" in error
    assert "secondary down" in error
    assert repository.saved == []
