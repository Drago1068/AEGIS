"""Unit tests for the Polygon.io daily-bar provider adapter."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from decimal import Decimal
from typing import Any

import httpx
import pytest

from aegis.config.settings import Settings
from aegis.providers.errors import (
    ProviderError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)
from aegis.providers.polygon import PolygonProvider

# 2024-01-02 00:00:00 America/New_York = 2024-01-02 05:00:00 UTC in standard time
_TS_2024_01_02 = 1_704_171_600_000
_TS_2024_01_03 = 1_704_258_000_000

_VALID_BODY = {
    "ticker": "AAPL",
    "adjusted": False,
    "status": "OK",
    "resultsCount": 2,
    "results": [
        {
            "o": 180.0,
            "h": 181.0,
            "l": 179.0,
            "c": 180.5,
            "v": 900000,
            "t": _TS_2024_01_02,
        },
        {
            "o": 185.0,
            "h": 186.5,
            "l": 184.0,
            "c": 185.75,
            "v": 1000000,
            "t": _TS_2024_01_03,
        },
    ],
}


def _make_provider(
    handler: Callable[[httpx.Request], httpx.Response],
    settings: Settings | None = None,
) -> PolygonProvider:
    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)
    effective_settings = settings or Settings(environment="test", polygon_api_key="test-key")
    return PolygonProvider(effective_settings, client)


def _json_handler(
    body: dict[str, Any], status_code: int = 200
) -> Callable[[httpx.Request], httpx.Response]:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "apiKey" not in request.url.params
        assert request.headers.get("Authorization") == "Bearer test-key"
        return httpx.Response(status_code, json=body)

    return handler


@pytest.mark.asyncio
async def test_fetch_daily_bars_parses_and_sorts_oldest_first() -> None:
    provider = _make_provider(_json_handler(_VALID_BODY))

    bars = await provider.fetch_daily_bars("AAPL")

    assert [bar.trading_date for bar in bars] == [date(2024, 1, 2), date(2024, 1, 3)]
    first = bars[0]
    assert first.symbol == "AAPL"
    assert first.open == Decimal("180.0")
    assert first.high == Decimal("181.0")
    assert first.low == Decimal("179.0")
    assert first.close == Decimal("180.5")
    assert first.volume == 900000
    assert first.raw_payload["trading_date"] == "2024-01-02"


@pytest.mark.asyncio
async def test_fetch_daily_bars_raises_without_api_key() -> None:
    provider = _make_provider(
        _json_handler(_VALID_BODY),
        settings=Settings(environment="test", polygon_api_key=None),
    )

    with pytest.raises(ProviderUnavailableError, match="API key"):
        await provider.fetch_daily_bars("AAPL")


@pytest.mark.asyncio
async def test_fetch_daily_bars_raises_unavailable_on_http_5xx() -> None:
    provider = _make_provider(_json_handler({}, status_code=503))

    with pytest.raises(ProviderUnavailableError, match="HTTP 503"):
        await provider.fetch_daily_bars("AAPL")


@pytest.mark.asyncio
async def test_fetch_daily_bars_raises_rate_limit_on_429() -> None:
    provider = _make_provider(_json_handler({}, status_code=429))

    with pytest.raises(ProviderRateLimitError, match="rate limit"):
        await provider.fetch_daily_bars("AAPL")


@pytest.mark.asyncio
async def test_fetch_daily_bars_raises_on_http_4xx() -> None:
    provider = _make_provider(_json_handler({}, status_code=404))

    with pytest.raises(ProviderError, match="HTTP 404"):
        await provider.fetch_daily_bars("AAPL")


@pytest.mark.asyncio
async def test_fetch_daily_bars_raises_on_transport_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    provider = _make_provider(handler)

    with pytest.raises(ProviderUnavailableError, match="request failed"):
        await provider.fetch_daily_bars("AAPL")


@pytest.mark.asyncio
async def test_fetch_daily_bars_raises_on_non_json_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not json")

    provider = _make_provider(handler)

    with pytest.raises(ProviderError, match="non-JSON"):
        await provider.fetch_daily_bars("AAPL")


@pytest.mark.asyncio
async def test_fetch_daily_bars_raises_on_error_status() -> None:
    provider = _make_provider(_json_handler({"status": "ERROR", "results": []}))

    with pytest.raises(ProviderError, match="error status"):
        await provider.fetch_daily_bars("AAPL")


@pytest.mark.asyncio
async def test_fetch_daily_bars_raises_on_malformed_bar() -> None:
    body = {
        "status": "OK",
        "results": [{"o": "bad", "h": 1, "l": 1, "c": 1, "v": 1, "t": _TS_2024_01_02}],
    }
    provider = _make_provider(_json_handler(body))

    with pytest.raises(ProviderError, match="malformed"):
        await provider.fetch_daily_bars("AAPL")


@pytest.mark.asyncio
async def test_fetch_daily_bars_returns_empty_when_results_missing() -> None:
    provider = _make_provider(_json_handler({"status": "OK"}))

    bars = await provider.fetch_daily_bars("AAPL")

    assert bars == []


@pytest.mark.asyncio
async def test_fetch_daily_bars_uses_adjusted_false() -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["adjusted"] = request.url.params.get("adjusted", "")
        return httpx.Response(200, json={"status": "OK", "results": []})

    provider = _make_provider(handler)
    await provider.fetch_daily_bars("AAPL")
    assert seen["adjusted"] == "false"
