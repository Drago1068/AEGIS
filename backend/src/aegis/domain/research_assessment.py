"""Research-only assessment foundations (method ``daily_bar_research_v1``).

Framework-free domain rules: compute research components and coverage confidence from stored
daily bars, or fail closed without inventing values. This is a research heuristic, not a
probability, recommendation, or trade signal. See ADR-0007 and ADR-0012.

Phase 6 (method_version 1) coverage::

    coverage_confidence = clip(bar_count_factor * freshness_factor * primary_fraction)

Phase 11 (method_version 2) extends with multi-source factors when enabled::

    coverage_confidence = clip(
      bar_count_factor * freshness_factor * primary_fraction
      * source_availability_factor * source_agreement_factor
    )

``probability_confidence`` is always ``None`` (not calibrated). The two confidences must
never be merged.
"""

from __future__ import annotations

import logging
import math
import statistics
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING, Protocol

from aegis.domain.calendars import is_trading_day, most_recent_trading_day

if TYPE_CHECKING:
    from aegis.domain.research_assessment_backfill import AssessmentBackfillSummary

logger = logging.getLogger(__name__)

METHOD_ID = "daily_bar_research_v1"
METHOD_VERSION_V1 = 1
METHOD_VERSION_V2 = 2
SCHEMA_VERSION_V1 = 1
SCHEMA_VERSION_V2 = 2
# Backward-compatible aliases for call sites that still import METHOD_VERSION / SCHEMA_VERSION.
METHOD_VERSION = METHOD_VERSION_V1
SCHEMA_VERSION = SCHEMA_VERSION_V1
LOOKBACK_SESSIONS = 20
STATE_RESEARCH_ONLY = "research_only"
ANNUALIZATION_FACTOR = math.sqrt(252)
VOLATILITY_EPSILON = 1e-12
# Load a buffer of recent bars so multi-source rows in the window do not starve the lookback.
BAR_LOAD_LIMIT = 120
PRIMARY_QUALITY = "primary"
MULTI_SOURCE_AGREEMENT_FLOOR = 0.80
COMPONENT_SOURCE_MIXED = "mixed"


class ResearchAssessmentReason(StrEnum):
    """Structured fail-closed reason codes for HTTP 422 ``detail.reason``."""

    INSUFFICIENT_PRIMARY_BARS = "insufficient_primary_bars"
    UNUSABLE_OHLCV = "unusable_ohlcv"
    STALE_LATEST_BAR = "stale_latest_bar"
    MULTI_SOURCE_DISAGREEMENT = "multi_source_disagreement"


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
class ResearchMultiSourceCoverageConfig:
    """Phase 11 multi-source coverage weighting options (ADR-0012)."""

    enabled: bool
    primary_source: str
    secondary_source: str | None
    close_tolerance: float
    disagreement_fail_closed: bool
    allow_cross_source_component_fill: bool


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
    components: dict[str, object]
    schema_version: int
    input_source: str
    lookback_start_date: date
    lookback_end_date: date
    bar_count: int
    id: int | None = None


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

    async def get_by_id(
        self, assessment_snapshot_id: int
    ) -> ResearchAssessmentSnapshotData | None:
        """Return the snapshot with ``assessment_snapshot_id``, or ``None``."""
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
    source_availability_factor: float = 1.0,
    source_agreement_factor: float = 1.0,
) -> float:
    """Product of coverage factors, clipped to ``[0, 1]``.

    Phase 6 uses the first three factors (availability/agreement default to 1). Phase 11
    multiplies the optional source factors when enabled. Exact formulas: ADR-0007 / ADR-0012.
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

    raw = (
        bar_count_factor
        * freshness_factor
        * primary_fraction
        * source_availability_factor
        * source_agreement_factor
    )
    return max(0.0, min(1.0, raw))


def coverage_factor_breakdown(
    *,
    usable_primary_bars: int,
    total_bars_in_lookback_window: int,
    latest_trading_date: date,
    calendar_name: str,
    as_of: date,
    max_staleness_trading_days: int,
    source_availability_factor: float = 1.0,
    source_agreement_factor: float = 1.0,
) -> dict[str, float]:
    """Return the individual factors used by :func:`compute_coverage_confidence`."""

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

    return {
        "bar_count_factor": bar_count_factor,
        "freshness_factor": freshness_factor,
        "primary_fraction": primary_fraction,
        "source_availability_factor": source_availability_factor,
        "source_agreement_factor": source_agreement_factor,
    }


def assess_from_bars(
    symbol: str,
    bars_newest_first: list[ResearchBarInput],
    *,
    calendar_name: str,
    max_latest_bar_staleness_trading_days: int,
    as_of: date | None = None,
    computed_at: datetime | None = None,
    multi_source: ResearchMultiSourceCoverageConfig | None = None,
) -> ResearchAssessmentSnapshotData:
    """Compute a research-only assessment or raise :class:`ResearchAssessmentUnavailableError`.

    ``bars_newest_first`` must be the recent stored series (any ``data_quality``). Persist
    nothing when this raises. When ``multi_source`` is None or disabled, Phase 6
    method_version 1 behavior is preserved.
    """

    if multi_source is not None and multi_source.enabled:
        return _assess_from_bars_v2(
            symbol,
            bars_newest_first,
            calendar_name=calendar_name,
            max_latest_bar_staleness_trading_days=max_latest_bar_staleness_trading_days,
            as_of=as_of,
            computed_at=computed_at,
            multi_source=multi_source,
        )
    return _assess_from_bars_v1(
        symbol,
        bars_newest_first,
        calendar_name=calendar_name,
        max_latest_bar_staleness_trading_days=max_latest_bar_staleness_trading_days,
        as_of=as_of,
        computed_at=computed_at,
    )


def _assess_from_bars_v1(
    symbol: str,
    bars_newest_first: list[ResearchBarInput],
    *,
    calendar_name: str,
    max_latest_bar_staleness_trading_days: int,
    as_of: date | None,
    computed_at: datetime | None,
) -> ResearchAssessmentSnapshotData:
    """Phase 6 path: any-source primary-quality series and three-factor coverage."""

    resolved_as_of = as_of or datetime.now(tz=UTC).date()
    resolved_computed_at = _resolve_computed_at(computed_at)

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
        method_version=METHOD_VERSION_V1,
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
        schema_version=SCHEMA_VERSION_V1,
        input_source=input_source,
        lookback_start_date=lookback_start,
        lookback_end_date=lookback_end,
        bar_count=LOOKBACK_SESSIONS,
    )


def _assess_from_bars_v2(
    symbol: str,
    bars_newest_first: list[ResearchBarInput],
    *,
    calendar_name: str,
    max_latest_bar_staleness_trading_days: int,
    as_of: date | None,
    computed_at: datetime | None,
    multi_source: ResearchMultiSourceCoverageConfig,
) -> ResearchAssessmentSnapshotData:
    """Phase 11 path: preferred-source components and multi-source coverage factors."""

    resolved_as_of = as_of or datetime.now(tz=UTC).date()
    resolved_computed_at = _resolve_computed_at(computed_at)
    chronological = sorted(bars_newest_first, key=lambda bar: bar.trading_date)

    window = _select_component_bars(
        chronological,
        primary_source=multi_source.primary_source,
        secondary_source=multi_source.secondary_source,
        allow_cross_source_fill=multi_source.allow_cross_source_component_fill,
    )

    lookback_start = window[0].trading_date
    lookback_end = window[-1].trading_date
    component_sources_used = {bar.source for bar in window}
    component_source = (
        next(iter(component_sources_used))
        if len(component_sources_used) == 1
        else COMPONENT_SOURCE_MIXED
    )

    configured_sources = _configured_research_sources(
        multi_source.primary_source, multi_source.secondary_source
    )

    # Primary fraction is scoped to component-source rows so dual vendor storage does not
    # spuriously halve coverage (ADR-0012).
    if component_source == COMPONENT_SOURCE_MIXED:
        component_source_filter = component_sources_used
    else:
        component_source_filter = {component_source}

    bars_in_component_window = [
        bar
        for bar in chronological
        if lookback_start <= bar.trading_date <= lookback_end
        and bar.source in component_source_filter
    ]
    usable_component_primary = [
        bar
        for bar in bars_in_component_window
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

    expected_dates = _trading_days_inclusive(
        lookback_start, lookback_end, calendar_name
    )
    availability, agreement, comparable_dates, agreeing_dates = (
        _multi_source_coverage_factors(
            chronological,
            expected_dates=expected_dates,
            configured_sources=configured_sources,
            close_tolerance=multi_source.close_tolerance,
        )
    )

    if (
        multi_source.disagreement_fail_closed
        and comparable_dates > 0
        and agreement < MULTI_SOURCE_AGREEMENT_FLOOR
    ):
        raise ResearchAssessmentUnavailableError(
            ResearchAssessmentReason.MULTI_SOURCE_DISAGREEMENT,
            (
                f"source agreement factor {agreement:.4f} below floor "
                f"{MULTI_SOURCE_AGREEMENT_FLOOR:.2f} "
                f"({agreeing_dates}/{comparable_dates} agreeing comparable dates)"
            ),
        )

    factors = coverage_factor_breakdown(
        usable_primary_bars=len(usable_component_primary),
        total_bars_in_lookback_window=len(bars_in_component_window),
        latest_trading_date=lookback_end,
        calendar_name=calendar_name,
        as_of=resolved_as_of,
        max_staleness_trading_days=max_latest_bar_staleness_trading_days,
        source_availability_factor=availability,
        source_agreement_factor=agreement,
    )
    coverage = compute_coverage_confidence(
        usable_primary_bars=len(usable_component_primary),
        total_bars_in_lookback_window=len(bars_in_component_window),
        latest_trading_date=lookback_end,
        calendar_name=calendar_name,
        as_of=resolved_as_of,
        max_staleness_trading_days=max_latest_bar_staleness_trading_days,
        source_availability_factor=availability,
        source_agreement_factor=agreement,
    )

    return ResearchAssessmentSnapshotData(
        symbol=symbol.upper(),
        method_id=METHOD_ID,
        method_version=METHOD_VERSION_V2,
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
            "component_source": component_source,
            "coverage_sources": list(configured_sources),
            "comparable_dates": comparable_dates,
            "agreeing_dates": agreeing_dates,
            **factors,
        },
        schema_version=SCHEMA_VERSION_V2,
        input_source=component_source,
        lookback_start_date=lookback_start,
        lookback_end_date=lookback_end,
        bar_count=LOOKBACK_SESSIONS,
    )


def _select_component_bars(
    chronological: list[ResearchBarInput],
    *,
    primary_source: str,
    secondary_source: str | None,
    allow_cross_source_fill: bool,
) -> list[ResearchBarInput]:
    """Select 20 usable primary-quality bars, preferring ``primary_source``."""

    primary_usable = [
        bar
        for bar in chronological
        if bar.source == primary_source
        and bar.data_quality == PRIMARY_QUALITY
        and is_usable_ohlcv(bar)
    ]
    if len(primary_usable) >= LOOKBACK_SESSIONS:
        return primary_usable[-LOOKBACK_SESSIONS:]

    if not allow_cross_source_fill or secondary_source is None:
        raise ResearchAssessmentUnavailableError(
            ResearchAssessmentReason.INSUFFICIENT_PRIMARY_BARS,
            (
                f"need {LOOKBACK_SESSIONS} usable primary bars from "
                f"{primary_source}, found {len(primary_usable)}"
            ),
        )

    secondary_usable = [
        bar
        for bar in chronological
        if bar.source == secondary_source
        and bar.data_quality == PRIMARY_QUALITY
        and is_usable_ohlcv(bar)
    ]
    by_date_primary = {bar.trading_date: bar for bar in primary_usable}
    by_date_secondary = {bar.trading_date: bar for bar in secondary_usable}
    all_dates = sorted(set(by_date_primary) | set(by_date_secondary))
    if len(all_dates) < LOOKBACK_SESSIONS:
        raise ResearchAssessmentUnavailableError(
            ResearchAssessmentReason.INSUFFICIENT_PRIMARY_BARS,
            (
                f"need {LOOKBACK_SESSIONS} usable primary bars from "
                f"{primary_source} (with optional {secondary_source} fill), "
                f"found {len(all_dates)} distinct session dates"
            ),
        )

    selected: list[ResearchBarInput] = []
    for trading_date in all_dates[-LOOKBACK_SESSIONS:]:
        if trading_date in by_date_primary:
            selected.append(by_date_primary[trading_date])
        else:
            selected.append(by_date_secondary[trading_date])
    return selected


def _configured_research_sources(
    primary_source: str, secondary_source: str | None
) -> list[str]:
    sources = [primary_source]
    if secondary_source is not None and secondary_source != primary_source:
        sources.append(secondary_source)
    return sources


def _multi_source_coverage_factors(
    chronological: list[ResearchBarInput],
    *,
    expected_dates: list[date],
    configured_sources: list[str],
    close_tolerance: float,
) -> tuple[float, float, int, int]:
    """Return availability, agreement, comparable_dates, agreeing_dates."""

    if not expected_dates:
        return 0.0, 1.0, 0, 0

    usable_by_date: dict[date, dict[str, Decimal]] = {}
    configured = set(configured_sources)
    for bar in chronological:
        if bar.source not in configured:
            continue
        if bar.data_quality != PRIMARY_QUALITY or not is_usable_ohlcv(bar):
            continue
        if bar.trading_date not in expected_dates:
            continue
        per_source = usable_by_date.setdefault(bar.trading_date, {})
        # First usable close per source/date wins (deterministic chronological pass).
        if bar.source not in per_source:
            per_source[bar.source] = bar.close

    dates_with_any = sum(1 for d in expected_dates if d in usable_by_date)
    availability = dates_with_any / len(expected_dates)

    comparable_dates = 0
    agreeing_dates = 0
    for trading_date in expected_dates:
        closes = usable_by_date.get(trading_date)
        if closes is None or len(closes) < 2:
            continue
        comparable_dates += 1
        values = list(closes.values())
        max_close = max(values)
        min_close = min(values)
        if max_close <= 0:
            continue
        relative_span = float((max_close - min_close) / max_close)
        if relative_span <= close_tolerance:
            agreeing_dates += 1

    agreement = (
        1.0 if comparable_dates == 0 else agreeing_dates / comparable_dates
    )

    return availability, agreement, comparable_dates, agreeing_dates


def _trading_days_inclusive(
    start: date, end: date, calendar_name: str
) -> list[date]:
    """Return exchange sessions from ``start`` through ``end`` inclusive."""

    if end < start:
        return []
    days: list[date] = []
    current = start
    while current <= end:
        if is_trading_day(current, calendar_name):
            days.append(current)
        current += timedelta(days=1)
    return days


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
        multi_source: ResearchMultiSourceCoverageConfig | None = None,
    ) -> None:
        self._bar_reader = bar_reader
        self._snapshot_store = snapshot_store
        self._calendar_name = calendar_name
        self._max_staleness = max_latest_bar_staleness_trading_days
        self._as_of = as_of
        self._multi_source = multi_source

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
                multi_source=self._multi_source,
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

    async def backfill_assessments(
        self, symbol: str, limit: int
    ) -> AssessmentBackfillSummary:
        """Create point-in-time assessments for recent primary bar dates (ADR-0046).

        Always returns a summary; individual fail-closed skips do not abort the batch.
        Does not run outcome labeling or calibration.
        """

        from aegis.domain.research_assessment_backfill import run_assessment_backfill

        normalized = symbol.upper()
        bars = await self._bar_reader.list_recent_bars(normalized, BAR_LOAD_LIMIT)
        # Bound existing-date lookup; backfill only considers candidates within loaded bars.
        existing_rows = await self._snapshot_store.list_recent(
            normalized, max(limit * 5, 100)
        )
        existing_as_of = {row.as_of_trading_date for row in existing_rows}
        return await run_assessment_backfill(
            normalized,
            bars_newest_first=bars,
            existing_as_of_dates=existing_as_of,
            limit=limit,
            calendar_name=self._calendar_name,
            max_latest_bar_staleness_trading_days=self._max_staleness,
            insert_snapshot=self._snapshot_store.insert,
            multi_source=self._multi_source,
        )


def _resolve_computed_at(computed_at: datetime | None) -> datetime:
    resolved = computed_at or datetime.now(tz=UTC)
    if resolved.tzinfo is None:
        return resolved.replace(tzinfo=UTC)
    return resolved


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
