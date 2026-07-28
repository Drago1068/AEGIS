"""Unit tests for daily-bar rejection rules.

Uses deterministic dates against the real NYSE calendar (via pandas-market-calendars) rather
than a fake calendar, since the calendar wrapper itself has no seams worth faking and NYSE
holidays/weekends are stable historical facts.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from aegis.domain.market_data_validation import RejectionReason, validate_daily_bar
from aegis.providers.market_data import DailyBar

_CALENDAR = "NYSE"

# 2024-01-02 is a Tuesday, a normal NYSE trading day.
_TRADING_DAY = date(2024, 1, 2)
# 2024-01-01 is New Year's Day, an NYSE holiday.
_HOLIDAY = date(2024, 1, 1)
# 2024-01-06 is a Saturday.
_WEEKEND = date(2024, 1, 6)


def _bar(**overrides: object) -> DailyBar:
    defaults: dict[str, object] = {
        "symbol": "AAPL",
        "trading_date": _TRADING_DAY,
        "open": Decimal("100"),
        "high": Decimal("110"),
        "low": Decimal("90"),
        "close": Decimal("105"),
        "volume": 1000,
        "raw_payload": {},
    }
    defaults.update(overrides)
    return DailyBar(**defaults)  # type: ignore[arg-type]


def _validate(bar: DailyBar, *, is_latest_bar: bool = False, as_of: date = _TRADING_DAY):
    return validate_daily_bar(
        bar,
        calendar_name=_CALENDAR,
        as_of=as_of,
        max_staleness_trading_days=3,
        is_latest_bar=is_latest_bar,
    )


def test_accepts_a_well_formed_bar() -> None:
    result = _validate(_bar())

    assert result.is_valid
    assert result.reason is None


def test_rejects_high_below_low_as_invalid() -> None:
    result = _validate(_bar(high=Decimal("80"), low=Decimal("90")))

    assert not result.is_valid
    assert result.reason is RejectionReason.INVALID


def test_rejects_high_below_open_as_invalid() -> None:
    result = _validate(_bar(open=Decimal("120"), high=Decimal("110")))

    assert not result.is_valid
    assert result.reason is RejectionReason.INVALID


def test_rejects_zero_price_as_non_positive() -> None:
    result = _validate(_bar(open=Decimal("0")))

    assert not result.is_valid
    assert result.reason is RejectionReason.NON_POSITIVE


def test_rejects_negative_price_as_non_positive() -> None:
    result = _validate(_bar(close=Decimal("-5")))

    assert not result.is_valid
    assert result.reason is RejectionReason.NON_POSITIVE


def test_rejects_negative_volume_as_non_positive() -> None:
    result = _validate(_bar(volume=-1))

    assert not result.is_valid
    assert result.reason is RejectionReason.NON_POSITIVE


def test_rejects_holiday_as_closed_session() -> None:
    result = _validate(_bar(trading_date=_HOLIDAY), as_of=_HOLIDAY)

    assert not result.is_valid
    assert result.reason is RejectionReason.CLOSED_SESSION


def test_rejects_weekend_as_closed_session() -> None:
    result = _validate(_bar(trading_date=_WEEKEND), as_of=_WEEKEND)

    assert not result.is_valid
    assert result.reason is RejectionReason.CLOSED_SESSION


def test_rejects_stale_latest_bar() -> None:
    old_bar = _bar(trading_date=date(2023, 12, 15))

    result = _validate(old_bar, is_latest_bar=True, as_of=_TRADING_DAY)

    assert not result.is_valid
    assert result.reason is RejectionReason.STALE


def test_does_not_reject_old_bar_when_not_latest() -> None:
    old_bar = _bar(trading_date=date(2023, 12, 15))

    result = _validate(old_bar, is_latest_bar=False, as_of=_TRADING_DAY)

    assert result.is_valid


def test_accepts_latest_bar_within_staleness_window() -> None:
    # 2023-12-29 is the last trading day before 2024-01-02 (weekend + New Year's Day between).
    recent_bar = _bar(trading_date=date(2023, 12, 29))

    result = _validate(recent_bar, is_latest_bar=True, as_of=_TRADING_DAY)

    assert result.is_valid
