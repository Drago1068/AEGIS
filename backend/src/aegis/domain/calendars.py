"""Thin wrapper around exchange trading-day calendars.

Per ADR-0002 and ``docs/architecture/market-data-contracts.md``, market-session and
trading-day determination must go through an explicit, swappable calendar abstraction rather
than naive wall-clock heuristics. This module is the only place that imports
``pandas_market_calendars`` directly; callers use these two functions.
"""

from __future__ import annotations

from datetime import date, timedelta
from functools import lru_cache
from typing import Any

import pandas_market_calendars as mcal  # pyright: ignore[reportMissingTypeStubs]

# pandas_market_calendars ships no type stubs (no py.typed marker), so its public surface is
# `Any` to pyright; the cast/ignore comments below make every crossing point explicit rather
# than letting Unknown silently propagate into the rest of the domain layer.

_LOOKBACK_DAYS_FOR_MOST_RECENT = 14


@lru_cache
def _get_calendar(calendar_name: str) -> Any:  # noqa: ANN401 - third-party type is untyped
    return mcal.get_calendar(calendar_name)  # pyright: ignore[reportUnknownMemberType]


def is_trading_day(trading_date: date, calendar_name: str) -> bool:
    """Return ``True`` if ``trading_date`` is a session day on the named exchange calendar."""

    calendar = _get_calendar(calendar_name)
    valid_days = calendar.valid_days(  # pyright: ignore[reportUnknownMemberType]
        start_date=trading_date, end_date=trading_date
    )
    return len(list(valid_days)) > 0


def most_recent_trading_day(as_of: date, calendar_name: str) -> date:
    """Return the most recent session day on or before ``as_of``.

    Raises:
        ValueError: no trading day was found in the lookback window, which would indicate a
            misconfigured calendar name rather than a normal holiday gap.
    """

    calendar = _get_calendar(calendar_name)
    start = as_of - timedelta(days=_LOOKBACK_DAYS_FOR_MOST_RECENT)
    valid_days = calendar.valid_days(  # pyright: ignore[reportUnknownMemberType]
        start_date=start, end_date=as_of
    )
    days = list(valid_days)
    if not days:
        raise ValueError(
            f"no trading day found for calendar {calendar_name!r} in the "
            f"{_LOOKBACK_DAYS_FOR_MOST_RECENT}-day window ending {as_of.isoformat()}"
        )
    return days[-1].date()  # pyright: ignore[reportUnknownMemberType]
