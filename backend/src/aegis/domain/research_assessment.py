"""Research-only assessment foundations (Phase 6, method ``daily_bar_research_v1``).

Framework-free domain rules: compute research components and coverage confidence from stored
daily bars, or fail closed without inventing values. This is a research heuristic, not a
probability, recommendation, or trade signal. See ADR-0007.

Coverage confidence formula (product, clipped to ``[0, 1]``)::

    bar_count_factor  = min(1, usable_primary_bars / 20)
    primary_fraction = usable_primary_bars / total_bars_in_lookback_window
    freshness_factor = 1 when latest trading_date >= expected latest session;
                       else 1 - (lag_trading_days / (max_staleness_trading_days + 1))
    coverage_confidence = clip(bar_count_factor * freshness_factor * primary_fraction)

``probability_confidence`` is always ``None`` in Phase 6 (not calibrated). The two
confidences must never be merged.
"""

from __future__ import annotations

import logging
import math
import statistics
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import Protocol

from aegis.domain.calendars import is_trading_day, most_recent_trading_day

logger = logging.getLogger(__name__)

METHOD_ID = "daily_bar_research_v1"
METHOD_VERSION = 1
SCHEMA_VERSION = 1
LOOKBACK_SESSIONS = 20
STATE_RESEARCH_ONLY = "research_only"
ANNUALIZATION_FACTOR = math.sqrt(252)
VOLATILITY_EPSILON = 1e-12
# Load a buffer of recent bars so non-primary rows in the window do not starve the lookback.
BAR_LOAD_LIMIT = 60
PRIMARY_QUALITY = "primary"


class ResearchAssessmentReason(StrEnum):
    """Structured fail-closed reason codes for HTTP 422 ``detail.reason``."""

    INSUFFICIENT_PRIMARY_BARS = "insufficient_primary_bars"
    UNUSABLE_OHLCV = "unusable_ohlcv"
    STALE_LATEST_BAR = "stale_latest_bar"


class ResearchAssessmentUnavailableError(Exception):
    """Raised when assessment inputs fail a gate; callers must persist nothing."""

    def __init__(self, reason: ResearchAssessmentReason, detail: str) -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(detail)


@dataclass(frozen=True, slots=True)
class ResearchBarInput:
    """One stored daily bar projected into the research assessment domain."""

    trading_date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    data_quality: str
    source: str


@dataclass(frozen=True, slots=True)
class ResearchAssessmentSnapshotData:
    """A successful research-only assessment ready for append-only persistence."""

    symbol: str
    method_id: str
    method_version: int
    state: str
    as_of_trading_date: date
    event_time: datetime
    computed_at: datetime
    coverage_confidence: float
    probability_confidence: float | None
    components: dict[str, float]
    schema_version: int
    input_source: str
    lookback_start_date: date
    lookback_end_date: date
    bar_count: int


class ResearchDailyBarReader(Protocol):
    """Read boundary for recent stored bars (newest-first)."""

    async def list_recent_bars(self, symbol: str, limit: int) -> list[ResearchBarInput]:
        """Return up to ``limit`` most recent bars for ``symbol``, newest first."""
        ...


class ResearchAssessmentStore(Protocol):
    """Append-only write/read boundary for research assessment snapshots."""

    async def insert(
        self, snapshot: ResearchAssessmentSnapshotData
    ) -> ResearchAssessmentSnapshotData:
        """Persist ``snapshot`` as a new row; never update in place."""
        ...

    async def list_recent(
        self, symbol: str, limit: int
    ) -> list[ResearchAssessmentSnapshotData]:
        """Return up to ``limit`` snapshots for ``symbol``, newest ``computed_at`` first."""
        ...

    async def get_latest(self, symbol: str) -> ResearchAssessmentSnapshotData | None:
        """Return the newest snapshot for ``symbol``, or ``None``."""
        ...


def is_usable_ohlcv(bar: ResearchBarInput) -> bool:
    """Return True when OHLCV values are positive and internally consistent."""

    if bar.open <= 0 or bar.high <= 0 or bar.low <= 0 or bar.close <= 0:
        return False
    if bar.volume < 0:
        return False
    if bar.high < bar.low:
        return False
    if bar.high < bar.open or bar.high < bar.close:
        return False
    return not (bar.low > bar.open or bar.low > bar.close)


def compute_total_return_20(closes: list[Decimal]) -> float:
    """``close_n / close_0 - 1`` over a 20-session close series (chronological)."""

    if len(closes) != LOOKBACK_SESSIONS:
        raise ValueError(f"expected {LOOKBACK_SESSIONS} closes, got {len(closes)}")
    first = closes[0]
    last = closes[-1]
    if first <= 0:
        raise ValueError("oldest close must be positive")
    return float(last / first - 1)


def compute_realized_vol_20(closes: list[Decimal]) -> float:
    """Annualized sample stdev of log returns over 19 intervals (``sqrt(252)``)."""

    if len(closes) != LOOKBACK_SESSIONS:
        raise ValueError(f"expected {LOOKBACK_SESSIONS} closes, got {len(closes)}")
    log_returns: list[float] = []
    for previous, current in zip(closes, closes[1:], strict=False):
        if previous <= 0 or current <= 0:
            raise ValueError("closes must be positive for log returns")
        log_returns.append(math.log(float(current / previous)))
    if len(log_returns) < 2:
        raise ValueError("need at least two log returns for sample stdev")
    return statistics.stdev(log_returns) * ANNUALIZATION_FACTOR


def compute_research_index(total_return_20: float, realized_vol_20: float) -> float:
    """``tanh(total_return_20 / max(realized_vol_20, epsilon))`` research heuristic."""

    denominator = max(realized_vol_20, VOLATILITY_EPSILON)
    return math.tanh(total_return_20 / denominator)


def compute_coverage_confidence(
    *,
    usable_primary_bars: int,
    total_bars_in_lookback_window: int,
    latest_trading_date: date,
    calendar_name: str,
    as_of: date,
    max_staleness_trading_days: int,
) -> float:
    """Product of bar-count, freshness, and primary-fraction factors, clipped to ``[0, 1]``.

    Exact formula is documented in the module docstring and ADR-0007.
    """

    bar_count_factor = min(1.0, usable_primary_bars / LOOKBACK_SESSIONS)
    if total_bars_in_lookback_window <= 0:
        primary_fraction = 0.0
    else:
        primary_fraction = usable_primary_bars / total_bars_in_lookback_window

    expected_latest = most_recent_trading_day(as_of, calendar_name)
    if latest_trading_date >= expected_latest:
        freshness_factor = 1.0
    else:
        lag = _count_trading_days_strictly_between(
            latest_trading_date, expected_latest, calendar_name
        )
        freshness_factor = max(
            0.0, 1.0 - (lag / (max_staleness_trading_days + 1))
        )

    raw = bar_count_factor * freshness_factor * primary_fraction
    return max(0.0, min(1.0, raw))


def assess_from_bars(
    symbol: str,
    bars_newest_first: list[ResearchBarInput],
    *,
    calendar_name: str,
    max_latest_bar_staleness_trading_days: int,
    as_of: date | None = None,
    computed_at: datetime | None = None,
) -> ResearchAssessmentSnapshotData:
    """Compute a research-only assessment or raise :class:`ResearchAssessmentUnavailableError`.

    ``bars_newest_first`` must be the recent stored series (any ``data_quality``). Persist
    nothing when this raises.
    """

    resolved_as_of = as_of or datetime.now(tz=UTC).date()
    resolved_computed_at = computed_at or datetime.now(tz=UTC)
    if resolved_computed_at.tzinfo is None:
        resolved_computed_at = resolved_computed_at.replace(tzinfo=UTC)

    chronological = sorted(bars_newest_first, key=lambda bar: bar.trading_date)
    primary_bars = [
        bar for bar in chronological if bar.data_quality == PRIMARY_QUALITY
    ]
    if len(primary_bars) < LOOKBACK_SESSIONS:
        raise ResearchAssessmentUnavailableError(
            ResearchAssessmentReason.INSUFFICIENT_PRIMARY_BARS,
            (
                f"need {LOOKBACK_SESSIONS} usable primary bars, "
                f"found {len(primary_bars)}"
            ),
        )

    window = primary_bars[-LOOKBACK_SESSIONS:]
    for bar in window:
        if not is_usable_ohlcv(bar):
            raise ResearchAssessmentUnavailableError(
                ResearchAssessmentReason.UNUSABLE_OHLCV,
                f"bar dated {bar.trading_date.isoformat()} has unusable OHLCV",
            )

    lookback_start = window[0].trading_date
    lookback_end = window[-1].trading_date
    bars_in_window = [
        bar
        for bar in chronological
        if lookback_start <= bar.trading_date <= lookback_end
    ]
    usable_primary_in_window = [
        bar
        for bar in bars_in_window
        if bar.data_quality == PRIMARY_QUALITY and is_usable_ohlcv(bar)
    ]

    latest = window[-1]
    _assert_latest_not_stale(
        latest,
        calendar_name=calendar_name,
        as_of=resolved_as_of,
        max_staleness_trading_days=max_latest_bar_staleness_trading_days,
    )

    closes = [bar.close for bar in window]
    total_return_20 = compute_total_return_20(closes)
    realized_vol_20 = compute_realized_vol_20(closes)
    research_index = compute_research_index(total_return_20, realized_vol_20)
    coverage = compute_coverage_confidence(
        usable_primary_bars=len(usable_primary_in_window),
        total_bars_in_lookback_window=len(bars_in_window),
        latest_trading_date=lookback_end,
        calendar_name=calendar_name,
        as_of=resolved_as_of,
        max_staleness_trading_days=max_latest_bar_staleness_trading_days,
    )

    sources = {bar.source for bar in window}
    input_source = sorted(sources)[0] if len(sources) == 1 else ",".join(sorted(sources))

    return ResearchAssessmentSnapshotData(
        symbol=symbol.upper(),
        method_id=METHOD_ID,
        method_version=METHOD_VERSION,
        state=STATE_RESEARCH_ONLY,
        as_of_trading_date=lookback_end,
        event_time=_session_event_time(lookback_end),
        computed_at=resolved_computed_at,
        coverage_confidence=coverage,
        probability_confidence=None,
        components={
            "total_return_20": total_return_20,
            "realized_vol_20": realized_vol_20,
            "research_index": research_index,
        },
        schema_version=SCHEMA_VERSION,
        input_source=input_source,
        lookback_start_date=lookback_start,
        lookback_end_date=lookback_end,
        bar_count=LOOKBACK_SESSIONS,
    )


class ResearchAssessmentService:
    """Load bars, compute a research-only assessment, and append a snapshot on success."""

    def __init__(
        self,
        bar_reader: ResearchDailyBarReader,
        snapshot_store: ResearchAssessmentStore,
        *,
        calendar_name: str,
        max_latest_bar_staleness_trading_days: int,
        as_of: date | None = None,
    ) -> None:
        self._bar_reader = bar_reader
        self._snapshot_store = snapshot_store
        self._calendar_name = calendar_name
        self._max_staleness = max_latest_bar_staleness_trading_days
        self._as_of = as_of

    async def assess(self, symbol: str) -> ResearchAssessmentSnapshotData:
        """Compute and persist one assessment for ``symbol``, or raise fail-closed."""

        bars = await self._bar_reader.list_recent_bars(symbol.upper(), BAR_LOAD_LIMIT)
        try:
            snapshot = assess_from_bars(
                symbol,
                bars,
                calendar_name=self._calendar_name,
                max_latest_bar_staleness_trading_days=self._max_staleness,
                as_of=self._as_of,
            )
        except ResearchAssessmentUnavailableError as exc:
            logger.info(
                "research_assessment_unavailable",
                extra={
                    "symbol": symbol.upper(),
                    "reason": exc.reason.value,
                    "detail": exc.detail,
                },
            )
            raise

        return await self._snapshot_store.insert(snapshot)

    async def list_assessments(
        self, symbol: str, limit: int
    ) -> list[ResearchAssessmentSnapshotData]:
        return await self._snapshot_store.list_recent(symbol.upper(), limit)

    async def latest_assessment(
        self, symbol: str
    ) -> ResearchAssessmentSnapshotData | None:
        return await self._snapshot_store.get_latest(symbol.upper())


def _assert_latest_not_stale(
    bar: ResearchBarInput,
    *,
    calendar_name: str,
    as_of: date,
    max_staleness_trading_days: int,
) -> None:
    if not is_trading_day(bar.trading_date, calendar_name):
        raise ResearchAssessmentUnavailableError(
            ResearchAssessmentReason.UNUSABLE_OHLCV,
            f"{bar.trading_date.isoformat()} is not a {calendar_name} trading day",
        )

    expected_latest = most_recent_trading_day(as_of, calendar_name)
    if bar.trading_date >= expected_latest:
        return

    lag = _count_trading_days_strictly_between(
        bar.trading_date, expected_latest, calendar_name
    )
    if lag > max_staleness_trading_days:
        raise ResearchAssessmentUnavailableError(
            ResearchAssessmentReason.STALE_LATEST_BAR,
            (
                f"latest bar dated {bar.trading_date.isoformat()} is {lag} "
                f"trading day(s) behind the expected latest session "
                f"{expected_latest.isoformat()}"
            ),
        )


def _count_trading_days_strictly_between(
    start: date, end: date, calendar_name: str
) -> int:
    """Count trading days strictly after ``start`` and up to and including ``end``."""

    count = 0
    current = start
    while current < end:
        current += timedelta(days=1)
        if is_trading_day(current, calendar_name):
            count += 1
    return count


def _session_event_time(trading_date: date) -> datetime:
    """UTC end-of-day placeholder for the as-of trading session."""

    return datetime.combine(trading_date, time(23, 59, 59), tzinfo=UTC)
