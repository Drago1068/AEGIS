"""Unit tests for provider revision detection (ADR-0013)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from aegis.domain.market_data_corrections import StoredBarSnapshot, bars_materially_differ
from aegis.providers.market_data import DailyBar


def _daily_bar(**overrides: object) -> DailyBar:
    defaults: dict[str, object] = {
        "symbol": "AAPL",
        "trading_date": date(2024, 1, 2),
        "open": Decimal("100"),
        "high": Decimal("110"),
        "low": Decimal("90"),
        "close": Decimal("105"),
        "volume": 1000,
        "raw_payload": {},
    }
    defaults.update(overrides)
    return DailyBar(**defaults)  # type: ignore[arg-type]


def _snapshot(**overrides: object) -> StoredBarSnapshot:
    defaults: dict[str, object] = {
        "id": 1,
        "trading_date": date(2024, 1, 2),
        "open": Decimal("100"),
        "high": Decimal("110"),
        "low": Decimal("90"),
        "close": Decimal("105"),
        "volume": 1000,
        "data_quality": "primary",
    }
    defaults.update(overrides)
    return StoredBarSnapshot(**defaults)  # type: ignore[arg-type]


def test_identical_bars_are_not_material() -> None:
    assert not bars_materially_differ(_snapshot(), _daily_bar())


def test_close_change_beyond_epsilon_is_material() -> None:
    incoming = _daily_bar(close=Decimal("106"))
    assert bars_materially_differ(_snapshot(), incoming)


def test_close_change_within_epsilon_is_not_material() -> None:
    incoming = _daily_bar(close=Decimal("105.0000001"))
    assert not bars_materially_differ(_snapshot(), incoming)


def test_volume_change_is_material() -> None:
    incoming = _daily_bar(volume=1001)
    assert bars_materially_differ(_snapshot(), incoming)


def test_data_quality_change_is_material() -> None:
    stored = _snapshot(data_quality="delayed")
    incoming = _daily_bar()
    assert bars_materially_differ(stored, incoming)
