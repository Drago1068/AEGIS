"""Unit tests for watchlist symbol normalization/validation."""

from __future__ import annotations

import pytest

from aegis.domain.watchlist import InvalidSymbolError, normalize_symbol


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("aapl", "AAPL"),
        (" AAPL ", "AAPL"),
        ("brk.b", "BRK.B"),
        ("rds-a", "RDS-A"),
        ("a", "A"),
        ("a" * 20, "A" * 20),
    ],
)
def test_valid_symbols_are_normalized(raw: str, expected: str) -> None:
    assert normalize_symbol(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "   ",
        "1AAPL",
        "AAPL!",
        "AAPL SPACE",
        "a" * 21,
        "$SPY",
    ],
)
def test_invalid_symbols_are_rejected(raw: str) -> None:
    with pytest.raises(InvalidSymbolError):
        normalize_symbol(raw)
