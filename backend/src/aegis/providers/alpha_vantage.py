"""Alpha Vantage ``TIME_SERIES_DAILY`` adapter.

Per ADR-0002, this is the first concrete :class:`~aegis.providers.market_data.DailyBarProvider`
implementation. Alpha Vantage returns HTTP 200 even when it is reporting an error (invalid
symbol, rate limit, or a premium-tier gate), so this adapter inspects the response body for
those shapes and raises a typed error instead of letting a caller mistake an error body for an
empty (but valid) result.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any, cast

import httpx

from aegis.config.settings import Settings
from aegis.providers.errors import ProviderError, ProviderRateLimitError
from aegis.providers.market_data import DailyBar

_FUNCTION = "TIME_SERIES_DAILY"
_TIME_SERIES_KEY = "Time Series (Daily)"

_FIELD_OPEN = "1. open"
_FIELD_HIGH = "2. high"
_FIELD_LOW = "3. low"
_FIELD_CLOSE = "4. close"
_FIELD_VOLUME = "5. volume"


class AlphaVantageProvider:
    """Fetches daily bars from Alpha Vantage over HTTP.

    The API key is read from settings at call time and is never included in any raised
    exception message or log statement; only the symbol and status are.
    """

    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self._settings = settings
        self._client = client

    async def fetch_daily_bars(self, symbol: str) -> list[DailyBar]:
        """Fetch and parse daily bars for ``symbol``, oldest first.

        Raises:
            ProviderError: the API key is unset, the HTTP request failed, the response body
                could not be parsed, or Alpha Vantage reported a non-rate-limit error.
            ProviderRateLimitError: Alpha Vantage reported a rate limit or premium-tier gate.
        """

        if not self._settings.alpha_vantage_api_key:
            raise ProviderError("Alpha Vantage API key is not configured")

        try:
            response = await self._client.get(
                self._settings.alpha_vantage_base_url,
                params={
                    "function": _FUNCTION,
                    "symbol": symbol,
                    "outputsize": self._settings.daily_bar_output_size,
                    "apikey": self._settings.alpha_vantage_api_key,
                },
            )
        except httpx.HTTPError as exc:
            raise ProviderError(f"Alpha Vantage request failed for {symbol!r}: {exc}") from exc

        if response.status_code != 200:
            raise ProviderError(
                f"Alpha Vantage returned HTTP {response.status_code} for {symbol!r}"
            )

        try:
            payload: dict[str, Any] = response.json()
        except ValueError as exc:
            raise ProviderError(
                f"Alpha Vantage returned a non-JSON response for {symbol!r}"
            ) from exc

        _raise_for_error_body(payload, symbol)

        time_series_raw = payload.get(_TIME_SERIES_KEY)
        if not isinstance(time_series_raw, dict) or not time_series_raw:
            raise ProviderError(
                f"Alpha Vantage response for {symbol!r} is missing {_TIME_SERIES_KEY!r}"
            )
        time_series = cast("dict[str, Any]", time_series_raw)

        bars = [
            _parse_bar(symbol, trading_date_str, fields)
            for trading_date_str, fields in time_series.items()
        ]
        bars.sort(key=lambda bar: bar.trading_date)
        return bars


def _raise_for_error_body(payload: dict[str, Any], symbol: str) -> None:
    """Raise a typed error if ``payload`` is one of Alpha Vantage's known error shapes."""

    error_message = payload.get("Error Message")
    if isinstance(error_message, str):
        raise ProviderError(f"Alpha Vantage error for {symbol!r}: {error_message}")

    rate_limit_message = payload.get("Note") or payload.get("Information")
    if isinstance(rate_limit_message, str):
        raise ProviderRateLimitError(
            f"Alpha Vantage rate limit or premium-tier gate for {symbol!r}: "
            f"{rate_limit_message}"
        )


def _parse_bar(symbol: str, trading_date_str: str, raw_fields: object) -> DailyBar:
    if not isinstance(raw_fields, dict):
        raise ProviderError(
            f"Alpha Vantage bar for {symbol!r} on {trading_date_str!r} is malformed"
        )
    fields = cast("dict[str, Any]", raw_fields)

    try:
        trading_date = date.fromisoformat(trading_date_str)
        return DailyBar(
            symbol=symbol,
            trading_date=trading_date,
            open=_decimal(fields, _FIELD_OPEN),
            high=_decimal(fields, _FIELD_HIGH),
            low=_decimal(fields, _FIELD_LOW),
            close=_decimal(fields, _FIELD_CLOSE),
            volume=int(fields[_FIELD_VOLUME]),
            raw_payload={"date": trading_date_str, **fields},
        )
    except (KeyError, ValueError, InvalidOperation, TypeError) as exc:
        raise ProviderError(
            f"Alpha Vantage bar for {symbol!r} on {trading_date_str!r} is malformed: {exc}"
        ) from exc


def _decimal(fields: dict[str, Any], key: str) -> Decimal:
    return Decimal(str(fields[key]))
