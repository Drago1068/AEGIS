"""Provider-agnostic market data types and the daily-bar provider interface."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class DailyBar:
    """A single raw daily OHLCV observation as parsed from a provider response.

    This is intentionally provider-agnostic and unvalidated: :mod:`aegis.domain` decides
    whether a given bar is usable. ``raw_payload`` preserves the provider's own representation
    of this bar for audit/provenance, per the append-only provenance requirement in
    ``docs/architecture/data-model.md``.
    """

    symbol: str
    trading_date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    raw_payload: dict[str, Any]


class DailyBarProvider(Protocol):
    """A source of daily OHLCV bars for a single symbol.

    Domain and orchestration code depends only on this protocol, never on a concrete provider
    SDK/client, so providers remain swappable per ADR-0002.
    """

    async def fetch_daily_bars(self, symbol: str) -> list[DailyBar]:
        """Return the available daily bars for ``symbol``, most providers newest-first.

        Raises:
            aegis.providers.errors.ProviderError: the provider returned an error or an
                unparsable response.
            aegis.providers.errors.ProviderRateLimitError: the provider reported a rate limit
                or a premium-tier gate.
        """
        ...
