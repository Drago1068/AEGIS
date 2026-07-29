"""Provider revision detection for daily bar observations (ADR-0013).

Framework-free comparison helpers live here so ingestion orchestration can decide between skip,
initial insert, and correction insert without SQLAlchemy imports.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from aegis.providers.market_data import DailyBar

DEFAULT_PRICE_EPSILON = Decimal("1e-6")


@dataclass(frozen=True, slots=True)
class StoredBarSnapshot:
    """Minimal fields from a current stored observation for revision comparison."""

    id: int
    trading_date: object  # date; kept loose for protocol compatibility in typing
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    data_quality: str


def _price_differs(
    stored: Decimal,
    incoming: Decimal,
    epsilon: Decimal,
) -> bool:
    if stored == incoming:
        return False
    reference = max(abs(stored), abs(incoming))
    if reference == 0:
        return stored != incoming
    return abs(stored - incoming) / reference > epsilon


def bars_materially_differ(
    stored: StoredBarSnapshot,
    incoming: DailyBar,
    *,
    price_epsilon: Decimal = DEFAULT_PRICE_EPSILON,
    incoming_data_quality: str = "primary",
) -> bool:
    """Return whether ``incoming`` should be stored as a correction vs ``stored``.

    Volume uses exact inequality. Prices use relative epsilon. Any ``data_quality`` change is
    material.
    """

    if stored.data_quality != incoming_data_quality:
        return True
    if stored.volume != incoming.volume:
        return True
    if _price_differs(stored.open, incoming.open, price_epsilon):
        return True
    if _price_differs(stored.high, incoming.high, price_epsilon):
        return True
    if _price_differs(stored.low, incoming.low, price_epsilon):
        return True
    return _price_differs(stored.close, incoming.close, price_epsilon)
