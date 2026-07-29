"""Unit tests for daily-bar provider registry."""

from __future__ import annotations

import httpx
import pytest

from aegis.config.settings import Settings
from aegis.providers.alpha_vantage import AlphaVantageProvider
from aegis.providers.polygon import PolygonProvider
from aegis.providers.registry import build_daily_bar_provider


def test_build_daily_bar_provider_selects_adapters() -> None:
    settings = Settings(environment="test")
    client = httpx.AsyncClient()

    assert isinstance(
        build_daily_bar_provider("alpha_vantage", settings, client), AlphaVantageProvider
    )
    assert isinstance(build_daily_bar_provider("polygon", settings, client), PolygonProvider)


def test_build_daily_bar_provider_rejects_unknown_source() -> None:
    settings = Settings(environment="test")
    client = httpx.AsyncClient()

    with pytest.raises(ValueError, match="unknown daily-bar provider source"):
        build_daily_bar_provider("finnhub", settings, client)  # type: ignore[arg-type]
