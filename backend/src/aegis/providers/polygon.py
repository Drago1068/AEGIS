"""Polygon.io daily aggregates adapter.

Per ADR-0011, this is the second concrete :class:`~aegis.providers.market_data.DailyBarProvider`
implementation. It calls ``GET /v2/aggs/ticker/{ticker}/range/1/day/{from}/{to}`` with
unadjusted bars (``adjusted=false``) so results align with Alpha Vantage
``TIME_SERIES_DAILY``. The API key is sent as ``Authorization: Bearer`` and never logged.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any, cast
from zoneinfo import ZoneInfo

import httpx

from aegis.config.settings import Settings
from aegis.providers.errors import (
    ProviderError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)
from aegis.providers.market_data import DailyBar

MARKET_DATA_SOURCE = "polygon"
"""The ``source`` value recorded against every bar this provider produces (see ADR-0011)."""

_ET = ZoneInfo("America/New_York")
_COMPACT_LOOKBACK_DAYS = 160
_FULL_LOOKBACK_DAYS = 730
_AGG_PATH = "/v2/aggs/ticker/{ticker}/range/1/day/{from_date}/{to_date}"


class PolygonProvider:
    """Fetches daily aggregate bars from Polygon.io over HTTP.

    The API key is read from settings at call time and is never included in any raised
    exception message or log statement.
    """

    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self._settings = settings
        self._client = client

    async def fetch_daily_bars(self, symbol: str) -> list[DailyBar]:
        """Fetch and parse daily bars for ``symbol``, oldest first.

        Raises:
            ProviderUnavailableError: API key unset, transport failure, or HTTP 5xx.
            ProviderRateLimitError: HTTP 429.
            ProviderError: other HTTP client errors, non-JSON body, ERROR status, or
                malformed bars.
        """

        if not self._settings.polygon_api_key:
            raise ProviderUnavailableError("Polygon API key is not configured")

        to_date = date.today()
        from_date = to_date - timedelta(days=_lookback_days(self._settings.daily_bar_output_size))
        path = _AGG_PATH.format(
            ticker=symbol,
            from_date=from_date.isoformat(),
            to_date=to_date.isoformat(),
        )
        url = f"{self._settings.polygon_base_url.rstrip('/')}{path}"

        try:
            response = await self._client.get(
                url,
                params={
                    "adjusted": "false",
                    "sort": "asc",
                    "limit": 50000,
                },
                headers={"Authorization": f"Bearer {self._settings.polygon_api_key}"},
            )
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError(
                f"Polygon request failed for {symbol!r}: {exc}"
            ) from exc

        if response.status_code == 429:
            raise ProviderRateLimitError(f"Polygon rate limit for {symbol!r}: HTTP 429")
        if response.status_code >= 500:
            raise ProviderUnavailableError(
                f"Polygon returned HTTP {response.status_code} for {symbol!r}"
            )
        if response.status_code != 200:
            raise ProviderError(
                f"Polygon returned HTTP {response.status_code} for {symbol!r}"
            )

        try:
            payload: dict[str, Any] = response.json()
        except ValueError as exc:
            raise ProviderError(
                f"Polygon returned a non-JSON response for {symbol!r}"
            ) from exc

        status = payload.get("status")
        if isinstance(status, str) and status.upper() not in {"OK", "DELAYED"}:
            raise ProviderError(
                f"Polygon error status for {symbol!r}: {status}"
            )

        results_raw = payload.get("results")
        if results_raw is None:
            return []
        if not isinstance(results_raw, list):
            raise ProviderError(
                f"Polygon response for {symbol!r} has a malformed results field"
            )

        bars = [_parse_bar(symbol, item) for item in cast("list[Any]", results_raw)]
        bars.sort(key=lambda bar: bar.trading_date)
        return bars


def _lookback_days(output_size: str) -> int:
    if output_size == "full":
        return _FULL_LOOKBACK_DAYS
    return _COMPACT_LOOKBACK_DAYS


def _parse_bar(symbol: str, raw_fields: object) -> DailyBar:
    if not isinstance(raw_fields, dict):
        raise ProviderError(f"Polygon bar for {symbol!r} is malformed")
    fields = cast("dict[str, Any]", raw_fields)

    try:
        timestamp_ms = fields["t"]
        if not isinstance(timestamp_ms, (int, float)):
            raise TypeError("aggregate timestamp must be numeric")
        trading_date = datetime.fromtimestamp(float(timestamp_ms) / 1000.0, tz=_ET).date()
        volume_raw = fields["v"]
        return DailyBar(
            symbol=symbol,
            trading_date=trading_date,
            open=_decimal(fields, "o"),
            high=_decimal(fields, "h"),
            low=_decimal(fields, "l"),
            close=_decimal(fields, "c"),
            volume=int(volume_raw),
            raw_payload={
                "t": timestamp_ms,
                "o": fields["o"],
                "h": fields["h"],
                "l": fields["l"],
                "c": fields["c"],
                "v": fields["v"],
                "trading_date": trading_date.isoformat(),
            },
        )
    except (KeyError, ValueError, InvalidOperation, TypeError, OSError) as exc:
        raise ProviderError(f"Polygon bar for {symbol!r} is malformed: {exc}") from exc


def _decimal(fields: dict[str, Any], key: str) -> Decimal:
    return Decimal(str(fields[key]))
