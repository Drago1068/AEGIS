"""Watchlist symbol validation.

Framework-free per the domain module boundary in ``docs/architecture/overview.md``: no
FastAPI or SQLAlchemy import belongs here. Used by the API schema layer
(``aegis.api.schemas.watchlist``) to validate user-submitted symbols before they ever reach
the persistence layer. See ``docs/architecture/decisions/0003-phase-2-scheduled-watchlist.md``.
"""

from __future__ import annotations

import re

_SYMBOL_PATTERN = re.compile(r"^[A-Z][A-Z0-9.\-]{0,19}$")


class InvalidSymbolError(ValueError):
    """Raised when a watchlist symbol does not match the required shape."""


def normalize_symbol(raw_symbol: str) -> str:
    """Return ``raw_symbol`` upper-cased and stripped, or raise if it is not a valid shape.

    A valid symbol starts with a letter, is 1-20 characters long, and otherwise contains only
    letters, digits, ``.``, or ``-`` (covers plain tickers like ``AAPL`` and share-class
    tickers like ``BRK.B``). This is a shape check only - it does not verify the symbol is a
    real, tradable instrument; that is discovered the next time ingestion runs.
    """

    symbol = raw_symbol.strip().upper()
    if not _SYMBOL_PATTERN.match(symbol):
        raise InvalidSymbolError(f"invalid watchlist symbol: {raw_symbol!r}")
    return symbol
