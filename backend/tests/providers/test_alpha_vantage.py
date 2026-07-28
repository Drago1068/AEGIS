"""Unit tests for the Alpha Vantage daily-bar provider adapter."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from decimal import Decimal
from typing import Any

import httpx
import pytest

from aegis.config.settings import Settings
from aegis.providers.alpha_vantage import AlphaVantageProvider
from aegis.providers.errors import ProviderError, ProviderRateLimitError

_VALID_BODY = {
    "Meta Data": {
        "2. Symbol": "AAPL",
    },
    "Time Series (Daily)": {
        "2024-01-02": {
            "1. open": "185.00",
            "2. high": "186.50",
            "3. low": "184.00",
            "4. close": "185.75",
            "5. volume": "1000000",
        },
        "2024-01-01": {
            "1. open": "180.00",
            "2. high": "181.00",
            "3. low": "179.00",
            "4. close": "180.50",
            "5. volume": "900000",
        },
    },
}


def _make_provider(
    handler: Callable[[httpx.Request], httpx.Response],
    settings: Settings | None = None,
) -> AlphaVantageProvider:
    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)
    effective_settings = settings or Settings(
        environment="test", alpha_vantage_api_key="test-key"
    )
    return AlphaVantageProvider(effective_settings, client)


def _json_handler(
    body: dict[str, Any], status_code: int = 200
) -> Callable[[httpx.Request], httpx.Response]:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=body)

    return handler


@pytest.mark.asyncio
async def test_fetch_daily_bars_parses_and_sorts_oldest_first() -> None:
    provider = _make_provider(_json_handler(_VALID_BODY))

    bars = await provider.fetch_daily_bars("AAPL")

    assert [bar.trading_date for bar in bars] == [date(2024, 1, 1), date(2024, 1, 2)]
    first = bars[0]
    assert first.symbol == "AAPL"
    assert first.open == Decimal("180.00")
    assert first.high == Decimal("181.00")
    assert first.low == Decimal("179.00")
    assert first.close == Decimal("180.50")
    assert first.volume == 900000
    assert first.raw_payload["date"] == "2024-01-01"


@pytest.mark.asyncio
async def test_fetch_daily_bars_raises_without_api_key() -> None:
    provider = _make_provider(
        _json_handler(_VALID_BODY),
        settings=Settings(environment="test", alpha_vantage_api_key=None),
    )

    with pytest.raises(ProviderError, match="API key"):
        await provider.fetch_daily_bars("AAPL")


@pytest.mark.asyncio
async def test_fetch_daily_bars_raises_on_http_error_status() -> None:
    provider = _make_provider(_json_handler({}, status_code=500))

    with pytest.raises(ProviderError, match="HTTP 500"):
        await provider.fetch_daily_bars("AAPL")


@pytest.mark.asyncio
async def test_fetch_daily_bars_raises_on_transport_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    provider = _make_provider(handler)

    with pytest.raises(ProviderError, match="request failed"):
        await provider.fetch_daily_bars("AAPL")


@pytest.mark.asyncio
async def test_fetch_daily_bars_raises_on_non_json_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not json")

    provider = _make_provider(handler)

    with pytest.raises(ProviderError, match="non-JSON"):
        await provider.fetch_daily_bars("AAPL")


@pytest.mark.asyncio
async def test_fetch_daily_bars_raises_on_malformed_payload() -> None:
    body = {"Time Series (Daily)": {"2024-01-01": {"1. open": "not-a-number"}}}
    provider = _make_provider(_json_handler(body))

    with pytest.raises(ProviderError, match="malformed"):
        await provider.fetch_daily_bars("AAPL")


@pytest.mark.asyncio
async def test_fetch_daily_bars_raises_on_missing_time_series() -> None:
    provider = _make_provider(_json_handler({"Meta Data": {}}))

    with pytest.raises(ProviderError, match="Time Series"):
        await provider.fetch_daily_bars("AAPL")


@pytest.mark.asyncio
async def test_fetch_daily_bars_raises_on_error_message() -> None:
    body = {"Error Message": "Invalid API call. Please retry or visit the documentation."}
    provider = _make_provider(_json_handler(body))

    with pytest.raises(ProviderError, match="Invalid API call"):
        await provider.fetch_daily_bars("BADSYMBOL")


@pytest.mark.asyncio
async def test_fetch_daily_bars_raises_rate_limit_on_note() -> None:
    body = {
        "Note": (
            "Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls "
            "per minute."
        )
    }
    provider = _make_provider(_json_handler(body))

    with pytest.raises(ProviderRateLimitError, match="rate limit"):
        await provider.fetch_daily_bars("AAPL")


@pytest.mark.asyncio
async def test_fetch_daily_bars_raises_rate_limit_on_information() -> None:
    body = {
        "Information": (
            "Thank you for using Alpha Vantage! This endpoint is upgraded to a premium plan."
        )
    }
    provider = _make_provider(_json_handler(body))

    with pytest.raises(ProviderRateLimitError):
        await provider.fetch_daily_bars("AAPL")
