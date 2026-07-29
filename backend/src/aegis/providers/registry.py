"""Factory for concrete :class:`~aegis.providers.market_data.DailyBarProvider` adapters."""

from __future__ import annotations

from typing import Final

import httpx

from aegis.config.settings import DAILY_BAR_SOURCE_IDS, DailyBarSourceId, Settings
from aegis.providers.alpha_vantage import AlphaVantageProvider
from aegis.providers.market_data import DailyBarProvider
from aegis.providers.polygon import PolygonProvider

KNOWN_DAILY_BAR_SOURCES: Final[frozenset[str]] = frozenset(DAILY_BAR_SOURCE_IDS)


def build_daily_bar_provider(
    source: DailyBarSourceId | str,
    settings: Settings,
    client: httpx.AsyncClient,
) -> DailyBarProvider:
    """Return the concrete daily-bar adapter for ``source``.

    Raises:
        ValueError: ``source`` is not a known daily-bar provider id.
    """

    if source == "alpha_vantage":
        return AlphaVantageProvider(settings, client)
    if source == "polygon":
        return PolygonProvider(settings, client)
    raise ValueError(f"unknown daily-bar provider source: {source!r}")
