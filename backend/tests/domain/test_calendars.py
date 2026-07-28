"""Unit tests for the exchange-calendar wrapper."""

from __future__ import annotations

from datetime import date

from aegis.domain.calendars import is_trading_day, most_recent_trading_day


def test_is_trading_day_true_for_normal_weekday() -> None:
    assert is_trading_day(date(2024, 1, 2), "NYSE") is True


def test_is_trading_day_false_for_weekend() -> None:
    assert is_trading_day(date(2024, 1, 6), "NYSE") is False


def test_is_trading_day_false_for_holiday() -> None:
    assert is_trading_day(date(2024, 1, 1), "NYSE") is False


def test_most_recent_trading_day_returns_same_day_when_trading_day() -> None:
    assert most_recent_trading_day(date(2024, 1, 2), "NYSE") == date(2024, 1, 2)


def test_most_recent_trading_day_skips_back_over_holiday_and_weekend() -> None:
    # 2024-01-01 is a holiday; the prior trading day is 2023-12-29 (Friday).
    assert most_recent_trading_day(date(2024, 1, 1), "NYSE") == date(2023, 12, 29)
