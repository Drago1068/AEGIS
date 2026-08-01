"""Research assessment outcome labels (Phase 13, ADR-0014).

Framework-free forward-return label computation from stored daily bars. Outcomes are evidence
for a future calibration phase; they are not probabilities, recommendations, or trade signals.
"""

from __future__ import annotations

import logging
from collections.abc import Container, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import Protocol

from aegis.domain.calendars import (
    count_trading_days_strictly_between,
    is_trading_day,
    most_recent_trading_day,
)
from aegis.domain.research_assessment import (
    COMPONENT_SOURCE_MIXED,
    STATE_RESEARCH_ONLY,
    ResearchAssessmentSnapshotData,
    ResearchBarInput,
)

logger = logging.getLogger(__name__)

LABEL_METHOD_ID = "forward_total_return_v1"
LABEL_METHOD_VERSION = 1
LABEL_SCHEMA_VERSION = 1
STATE_RESEARCH_ONLY_LABEL = STATE_RESEARCH_ONLY

FORWARD_HORIZON_SESSIONS: tuple[int, ...] = (5, 20)


class OutcomeLabelReason(StrEnum):
    """Structured fail-closed reason codes for HTTP 422 ``detail.reason``."""

    ASSESSMENT_NOT_FOUND = "assessment_not_found"
    NO_AS_OF_BAR = "no_as_of_bar"
    INSUFFICIENT_FORWARD_BARS = "insufficient_forward_bars"


class OutcomeLabelUnavailableError(Exception):
    """Raised when labels cannot be computed; callers must persist nothing."""

    def __init__(self, reason: OutcomeLabelReason, detail: str) -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(detail)


@dataclass(frozen=True, slots=True)
class OutcomeLabelData:
    """A successful outcome label row ready for append-only persistence."""

    assessment_snapshot_id: int
    symbol: str
    label_method_id: str
    label_method_version: int
    state: str
    as_of_trading_date: date
    computed_at: datetime
    labels: dict[str, float]
    label_end_dates: dict[str, str]
    schema_version: int
    bar_source: str
    id: int | None = None


class OutcomeLabelStore(Protocol):
    """Append-only persistence for outcome labels."""

    async def insert(self, label: OutcomeLabelData) -> OutcomeLabelData:
        """Persist a new label row."""
        ...

    async def get_latest_for_assessment(
        self, assessment_snapshot_id: int
    ) -> OutcomeLabelData | None:
        """Return the newest label for ``assessment_snapshot_id``, or ``None``."""
        ...

    async def list_for_assessment(
        self,
        assessment_snapshot_id: int,
        limit: int,
        *,
        symbol: str | None = None,
    ) -> list[OutcomeLabelData]:
        """Return up to ``limit`` labels for an assessment, newest first."""
        ...

    async def assessment_ids_with_labels(
        self,
        symbol: str,
        assessment_ids: Sequence[int],
        *,
        label_method_id: str,
    ) -> set[int]:
        """Return the subset of ``assessment_ids`` that already have a label row."""
        ...


def compute_forward_total_return_labels(
    snapshot: ResearchAssessmentSnapshotData,
    bars: list[ResearchBarInput],
    *,
    calendar_name: str,
    horizons: tuple[int, ...] = FORWARD_HORIZON_SESSIONS,
) -> OutcomeLabelData:
    """Compute forward total return labels for ``snapshot`` or raise fail-closed.

    Uses stored bars only. Persists nothing on failure; callers append on success.
    """

    if snapshot.id is None:
        raise OutcomeLabelUnavailableError(
            OutcomeLabelReason.ASSESSMENT_NOT_FOUND,
            "assessment snapshot id is required to attach outcome labels",
        )

    bar_source = _resolve_label_bar_source(snapshot, bars)
    as_of_close = _close_on_date(
        bars,
        snapshot.as_of_trading_date,
        bar_source,
    )
    if as_of_close is None:
        raise OutcomeLabelUnavailableError(
            OutcomeLabelReason.NO_AS_OF_BAR,
            (
                f"no usable close for {snapshot.symbol!r} on "
                f"{snapshot.as_of_trading_date.isoformat()} "
                f"(source={bar_source!r})"
            ),
        )

    closes_by_date = _index_closes(bars, bar_source)
    labels: dict[str, float] = {}
    label_end_dates: dict[str, str] = {}

    for horizon in horizons:
        end_date = _nth_trading_session_after(
            snapshot.as_of_trading_date,
            horizon,
            calendar_name,
        )
        end_close = closes_by_date.get(end_date)
        if end_close is None:
            raise OutcomeLabelUnavailableError(
                OutcomeLabelReason.INSUFFICIENT_FORWARD_BARS,
                (
                    f"need close on horizon end {end_date.isoformat()} "
                    f"({horizon} sessions after {snapshot.as_of_trading_date.isoformat()})"
                ),
            )
        key = f"forward_return_{horizon}"
        labels[key] = float(end_close / as_of_close - Decimal(1))
        label_end_dates[key] = end_date.isoformat()

    computed_at = datetime.now(tz=UTC)
    return OutcomeLabelData(
        assessment_snapshot_id=snapshot.id,
        symbol=snapshot.symbol,
        label_method_id=LABEL_METHOD_ID,
        label_method_version=LABEL_METHOD_VERSION,
        state=STATE_RESEARCH_ONLY_LABEL,
        as_of_trading_date=snapshot.as_of_trading_date,
        computed_at=computed_at,
        labels=labels,
        label_end_dates=label_end_dates,
        schema_version=LABEL_SCHEMA_VERSION,
        bar_source=bar_source,
    )


def resolve_label_bar_source(
    snapshot: ResearchAssessmentSnapshotData,
    bars: Sequence[ResearchBarInput] | None = None,
) -> str:
    """Resolve the observation source used for Phase 13 label closes (ADR-0014 / ADR-0058).

    When the assessment component series is truly ``mixed``, and ``bars`` are provided,
    prefer the first ``coverage_sources`` entry that has an as-of close, else any usable
    as-of bar's source (Phase 65). Without bars, ``mixed`` is returned so callers fail
    closed rather than inventing a source.
    """

    if snapshot.input_source != COMPONENT_SOURCE_MIXED:
        return snapshot.input_source
    component_source = snapshot.components.get("component_source")
    if isinstance(component_source, str) and component_source != COMPONENT_SOURCE_MIXED:
        return component_source
    if bars is not None:
        return _resolve_mixed_as_of_bar_source(snapshot, bars)
    return COMPONENT_SOURCE_MIXED


def _resolve_mixed_as_of_bar_source(
    snapshot: ResearchAssessmentSnapshotData,
    bars: Sequence[ResearchBarInput],
) -> str:
    """Pick a concrete bar source for a mixed component series from as-of provenance."""

    as_of = snapshot.as_of_trading_date
    preferred: list[str] = []
    raw_coverage = snapshot.components.get("coverage_sources")
    if isinstance(raw_coverage, list):
        preferred = [item for item in raw_coverage if isinstance(item, str) and item.strip()]
    bar_list = list(bars)
    for source in preferred:
        if _close_on_date(bar_list, as_of, source) is not None:
            return source
    for bar in bar_list:
        if bar.trading_date != as_of:
            continue
        if bar.close <= 0:
            continue
        return bar.source
    return COMPONENT_SOURCE_MIXED


def _resolve_label_bar_source(
    snapshot: ResearchAssessmentSnapshotData,
    bars: Sequence[ResearchBarInput] | None = None,
) -> str:
    return resolve_label_bar_source(snapshot, bars)


def _index_closes(
    bars: list[ResearchBarInput],
    source: str,
) -> dict[date, Decimal]:
    indexed: dict[date, Decimal] = {}
    for bar in bars:
        if bar.source != source:
            continue
        if bar.close <= 0:
            continue
        indexed[bar.trading_date] = bar.close
    return indexed


def _close_on_date(
    bars: list[ResearchBarInput],
    trading_date: date,
    source: str,
) -> Decimal | None:
    for bar in bars:
        if bar.trading_date != trading_date:
            continue
        if bar.source != source:
            continue
        if bar.close <= 0:
            continue
        return bar.close
    return None


def _nth_trading_session_after(
    start: date,
    n: int,
    calendar_name: str,
) -> date:
    if n <= 0:
        raise ValueError("horizon must be positive")
    count = 0
    current = start
    while count < n:
        current += timedelta(days=1)
        if is_trading_day(current, calendar_name):
            count += 1
    return current


def forward_horizon_end_date(
    as_of: date,
    horizon_sessions: int,
    calendar_name: str,
) -> date:
    """Return the exchange session ``horizon_sessions`` after ``as_of`` (Phase 13)."""

    return _nth_trading_session_after(as_of, horizon_sessions, calendar_name)


def has_stored_forward_horizon_close(
    as_of: date,
    closes_by_date: Container[date],
    *,
    calendar_name: str,
    min_forward_sessions: int | None = None,
) -> bool:
    """True when ``closes_by_date`` has the max (or requested) forward-horizon end close."""

    horizon = (
        min_forward_sessions
        if min_forward_sessions is not None
        else max(FORWARD_HORIZON_SESSIONS)
    )
    end_date = forward_horizon_end_date(as_of, horizon, calendar_name)
    return end_date in closes_by_date


def snapshot_label_block_reason(
    snapshot: ResearchAssessmentSnapshotData,
    bars: Sequence[ResearchBarInput],
    *,
    calendar_name: str,
    horizons: tuple[int, ...] = FORWARD_HORIZON_SESSIONS,
) -> OutcomeLabelReason | None:
    """Return the fail-closed label gate reason for ``snapshot``, or None when ready.

    Aligns with :func:`compute_forward_total_return_labels` / :func:`is_snapshot_label_ready`
    (ADR-0234). Never invents closes.
    """

    bar_source = _resolve_label_bar_source(snapshot, bars)
    closes_by_date = _index_closes(list(bars), bar_source)
    if snapshot.as_of_trading_date not in closes_by_date:
        return OutcomeLabelReason.NO_AS_OF_BAR
    for horizon in horizons:
        end_date = forward_horizon_end_date(snapshot.as_of_trading_date, horizon, calendar_name)
        if end_date not in closes_by_date:
            return OutcomeLabelReason.INSUFFICIENT_FORWARD_BARS
    return None


def snapshot_forward_bar_shortfall(
    snapshot: ResearchAssessmentSnapshotData,
    bars: Sequence[ResearchBarInput],
    *,
    calendar_name: str,
    horizons: tuple[int, ...] = FORWARD_HORIZON_SESSIONS,
) -> int | None:
    """Return trading sessions still needed for the max forward horizon (ADR-0246).

    Returns ``0`` when label-ready, ``None`` when there is no as_of close (shortfall not
    applicable). Never invents closes.
    """

    bar_source = _resolve_label_bar_source(snapshot, bars)
    closes_by_date = _index_closes(list(bars), bar_source)
    as_of = snapshot.as_of_trading_date
    if as_of not in closes_by_date:
        return None
    max_horizon = max(horizons)
    required_end = forward_horizon_end_date(as_of, max_horizon, calendar_name)
    if all(
        forward_horizon_end_date(as_of, horizon, calendar_name) in closes_by_date
        for horizon in horizons
    ):
        return 0
    forward_or_as_of = [day for day in closes_by_date if day >= as_of]
    last_available = max(forward_or_as_of)
    if last_available >= required_end:
        # Gap: later bars exist but required end close is missing.
        before_required = [day for day in forward_or_as_of if day < required_end]
        last_before = max(before_required) if before_required else as_of
        return count_trading_days_strictly_between(
            last_before, required_end, calendar_name
        )
    return count_trading_days_strictly_between(
        last_available, required_end, calendar_name
    )


def snapshot_required_label_end_date(
    snapshot: ResearchAssessmentSnapshotData,
    bars: Sequence[ResearchBarInput],
    *,
    calendar_name: str,
    horizons: tuple[int, ...] = FORWARD_HORIZON_SESSIONS,
) -> date | None:
    """Return the trading date that unlocks max-horizon labeling (ADR-0248).

    Calendar projection from stored as_of only. Returns ``None`` when there is no
    as_of close (end date not applicable). Never invents closes.
    """

    bar_source = _resolve_label_bar_source(snapshot, bars)
    closes_by_date = _index_closes(list(bars), bar_source)
    as_of = snapshot.as_of_trading_date
    if as_of not in closes_by_date:
        return None
    return forward_horizon_end_date(as_of, max(horizons), calendar_name)


def snapshot_last_available_label_bar_date(
    snapshot: ResearchAssessmentSnapshotData,
    bars: Sequence[ResearchBarInput],
    *,
    calendar_name: str,
    horizons: tuple[int, ...] = FORWARD_HORIZON_SESSIONS,
) -> date | None:
    """Return max stored close date on the label source with day >= as_of (ADR-0250).

    Includes as_of when no forward closes yet. Returns ``None`` when there is no as_of
    close. Never invents closes. ``calendar_name`` / ``horizons`` are unused but kept
    for call-site parity with sibling diagnostics.
    """

    _ = calendar_name, horizons
    bar_source = _resolve_label_bar_source(snapshot, bars)
    closes_by_date = _index_closes(list(bars), bar_source)
    as_of = snapshot.as_of_trading_date
    if as_of not in closes_by_date:
        return None
    forward_or_as_of = [day for day in closes_by_date if day >= as_of]
    return max(forward_or_as_of)


def snapshot_label_source_max_bar_date(
    snapshot: ResearchAssessmentSnapshotData,
    bars: Sequence[ResearchBarInput],
    *,
    calendar_name: str = "NYSE",
) -> date | None:
    """Return absolute max stored close date on the resolved label bar source (ADR-0256).

    Not filtered to ``day >= as_of``. Returns ``None`` when the source has no usable
    closes. Never invents closes. ``calendar_name`` unused; kept for call-site parity.
    """

    _ = calendar_name
    bar_source = _resolve_label_bar_source(snapshot, bars)
    closes_by_date = _index_closes(list(bars), bar_source)
    if not closes_by_date:
        return None
    return max(closes_by_date)


def stored_bar_calendar_lag_trading_days(
    snapshot: ResearchAssessmentSnapshotData,
    bars: Sequence[ResearchBarInput],
    *,
    calendar_name: str,
    reference_date: date,
) -> int | None:
    """Return sessions the label-source tip lags the prior completed session (ADR-0256).

    Tip is the absolute max stored close on the resolved label source. Reference is
    ``most_recent_trading_day(reference_date)``. Returns ``0`` when tip is current;
    ``None`` when no tip. Never invents closes.
    """

    tip = snapshot_label_source_max_bar_date(
        snapshot,
        bars,
        calendar_name=calendar_name,
    )
    if tip is None:
        return None
    expected = most_recent_trading_day(reference_date, calendar_name)
    if tip >= expected:
        return 0
    return count_trading_days_strictly_between(tip, expected, calendar_name)


def is_snapshot_label_ready(
    snapshot: ResearchAssessmentSnapshotData,
    bars: Sequence[ResearchBarInput],
    *,
    calendar_name: str,
    horizons: tuple[int, ...] = FORWARD_HORIZON_SESSIONS,
) -> bool:
    """True when compute gates for ``snapshot`` would succeed with ``bars`` (ADR-0058).

    Uses the same resolved ``bar_source`` as :func:`compute_forward_total_return_labels`
    so cross-source calendar presence does not mark a row ready when that source lacks
    as-of or forward-horizon closes.
    """

    return (
        snapshot_label_block_reason(
            snapshot,
            bars,
            calendar_name=calendar_name,
            horizons=horizons,
        )
        is None
    )


def ready_forward_horizons(
    snapshot: ResearchAssessmentSnapshotData,
    bars: Sequence[ResearchBarInput],
    *,
    calendar_name: str,
    horizons: tuple[int, ...] = FORWARD_HORIZON_SESSIONS,
) -> tuple[int, ...]:
    """Return the subset of ``horizons`` that individually pass label compute gates.

    Never invents closes. Empty when as-of is missing or no horizon end close is stored
    (ADR-0310). Order matches ``horizons``.
    """

    ready: list[int] = []
    for horizon in horizons:
        if is_snapshot_label_ready(
            snapshot,
            bars,
            calendar_name=calendar_name,
            horizons=(horizon,),
        ):
            ready.append(horizon)
    return tuple(ready)


class OutcomeLabelService:
    """Load assessment + bars, compute labels, append on success."""

    def __init__(
        self,
        assessment_store: ResearchAssessmentStoreForLabels,
        bar_reader: ResearchBarReaderForLabels,
        label_store: OutcomeLabelStore,
        *,
        calendar_name: str,
        bar_load_limit: int = 120,
    ) -> None:
        self._assessment_store = assessment_store
        self._bar_reader = bar_reader
        self._label_store = label_store
        self._calendar_name = calendar_name
        self._bar_load_limit = bar_load_limit

    async def label_assessment(self, symbol: str, assessment_snapshot_id: int) -> OutcomeLabelData:
        snapshot = await self._assessment_store.get_by_id(assessment_snapshot_id)
        if snapshot is None or snapshot.symbol.upper() != symbol.upper():
            raise OutcomeLabelUnavailableError(
                OutcomeLabelReason.ASSESSMENT_NOT_FOUND,
                f"no assessment {assessment_snapshot_id} for symbol {symbol!r}",
            )

        bars = await self._bar_reader.list_recent_bars(symbol.upper(), self._bar_load_limit)
        label = compute_forward_total_return_labels(
            snapshot,
            bars,
            calendar_name=self._calendar_name,
        )
        logger.info(
            "research_outcome_label_computed",
            extra={
                "symbol": symbol.upper(),
                "assessment_snapshot_id": assessment_snapshot_id,
                "horizons": list(label.labels.keys()),
            },
        )
        return await self._label_store.insert(label)

    async def label_assessment_ready_horizons(
        self, symbol: str, assessment_snapshot_id: int
    ) -> OutcomeLabelData:
        """Compute labels only for individually ready horizons (ADR-0310).

        Explicit opt-in when the full horizon set is tip-blocked. Fail-closed when no
        configured horizon is ready. Never invents bars; does not change
        :meth:`label_assessment`.
        """

        snapshot = await self._assessment_store.get_by_id(assessment_snapshot_id)
        if snapshot is None or snapshot.symbol.upper() != symbol.upper():
            raise OutcomeLabelUnavailableError(
                OutcomeLabelReason.ASSESSMENT_NOT_FOUND,
                f"no assessment {assessment_snapshot_id} for symbol {symbol!r}",
            )

        bars = await self._bar_reader.list_recent_bars(symbol.upper(), self._bar_load_limit)
        bar_source = _resolve_label_bar_source(snapshot, bars)
        closes_by_date = _index_closes(list(bars), bar_source)
        if snapshot.as_of_trading_date not in closes_by_date:
            raise OutcomeLabelUnavailableError(
                OutcomeLabelReason.NO_AS_OF_BAR,
                (
                    f"no usable close for {snapshot.symbol!r} on "
                    f"{snapshot.as_of_trading_date.isoformat()} "
                    f"(source={bar_source!r})"
                ),
            )

        ready = ready_forward_horizons(
            snapshot,
            bars,
            calendar_name=self._calendar_name,
        )
        if not ready:
            raise OutcomeLabelUnavailableError(
                OutcomeLabelReason.INSUFFICIENT_FORWARD_BARS,
                (
                    "no configured forward horizons are label-ready for "
                    f"assessment {assessment_snapshot_id} "
                    f"(as_of={snapshot.as_of_trading_date.isoformat()}); "
                    "ready-horizons path fail-closed"
                ),
            )

        label = compute_forward_total_return_labels(
            snapshot,
            bars,
            calendar_name=self._calendar_name,
            horizons=ready,
        )
        logger.info(
            "research_outcome_label_ready_horizons_computed",
            extra={
                "symbol": symbol.upper(),
                "assessment_snapshot_id": assessment_snapshot_id,
                "horizons": list(label.labels.keys()),
                "ready_sessions": list(ready),
            },
        )
        return await self._label_store.insert(label)

    async def is_assessment_label_ready(
        self, symbol: str, snapshot: ResearchAssessmentSnapshotData
    ) -> bool:
        """Return whether ``snapshot`` has stored forward closes needed to label (ADR-0232)."""

        ready, _reason = await self.label_readiness_for_assessment(symbol, snapshot)
        return ready

    async def label_readiness_for_assessment(
        self, symbol: str, snapshot: ResearchAssessmentSnapshotData
    ) -> tuple[bool, OutcomeLabelReason | None]:
        """Return ``(ready, block_reason)`` using stored bars (ADR-0232 / ADR-0234)."""

        bars = await self._bar_reader.list_recent_bars(symbol.upper(), self._bar_load_limit)
        reason = snapshot_label_block_reason(
            snapshot,
            bars,
            calendar_name=self._calendar_name,
        )
        return reason is None, reason

    async def resolve_label_bar_source_for_assessment(
        self,
        symbol: str,
        snapshot: ResearchAssessmentSnapshotData,
    ) -> str:
        """Resolve label bar source with stored bars (ADR-0066 / ADR-0268).

        Loads bars so true-mixed assessments get a concrete source when as-of closes
        exist. Returns ``mixed`` only when unresolved. Never invents sources.
        """

        bars = await self._bar_reader.list_recent_bars(symbol.upper(), self._bar_load_limit)
        return resolve_label_bar_source(snapshot, bars)

    async def scan_label_diagnostics(
        self,
        symbol: str,
        snapshots_newest_first: list[ResearchAssessmentSnapshotData],
        *,
        labeled_assessment_ids: set[int] | None = None,
        reference_date: date | None = None,
    ) -> tuple[
        bool | None,
        OutcomeLabelReason | None,
        date | None,
        date | None,
        int,
        int | None,
        date | None,
        date | None,
        int | None,
        date | None,
        int | None,
    ]:
        """Return readiness, dates, counts, unlock diagnostics, and calendar lag.

        Loads stored bars once (ADR-0232…0250/0252/0254/0256). Empty scan returns
        ``(None, None, None, None, 0, None, None, None, None, None, None)``.
        """

        if not snapshots_newest_first:
            return None, None, None, None, 0, None, None, None, None, None, None

        bars = await self._bar_reader.list_recent_bars(symbol.upper(), self._bar_load_limit)
        if labeled_assessment_ids is None:
            ids = [row.id for row in snapshots_newest_first if row.id is not None]
            labeled_assessment_ids = (
                await self.assessment_ids_with_labels(symbol, ids) if ids else set()
            )
        latest = snapshots_newest_first[0]
        block_reason = snapshot_label_block_reason(
            latest,
            bars,
            calendar_name=self._calendar_name,
        )
        forward_bar_shortfall = snapshot_forward_bar_shortfall(
            latest,
            bars,
            calendar_name=self._calendar_name,
        )
        min_horizon = min(FORWARD_HORIZON_SESSIONS)
        min_horizon_forward_bar_shortfall = snapshot_forward_bar_shortfall(
            latest,
            bars,
            calendar_name=self._calendar_name,
            horizons=(min_horizon,),
        )
        required_label_end_date = snapshot_required_label_end_date(
            latest,
            bars,
            calendar_name=self._calendar_name,
        )
        min_horizon_required_label_end_date = snapshot_required_label_end_date(
            latest,
            bars,
            calendar_name=self._calendar_name,
            horizons=(min_horizon,),
        )
        last_available_label_bar_date = snapshot_last_available_label_bar_date(
            latest,
            bars,
            calendar_name=self._calendar_name,
        )
        calendar_ref = reference_date if reference_date is not None else datetime.now(tz=UTC).date()
        calendar_lag = stored_bar_calendar_lag_trading_days(
            latest,
            bars,
            calendar_name=self._calendar_name,
            reference_date=calendar_ref,
        )
        most_recent_labelable: date | None = None
        most_recent_unlabeled_labelable: date | None = None
        unlabeled_label_ready_count = 0
        for row in snapshots_newest_first:
            if not is_snapshot_label_ready(
                row,
                bars,
                calendar_name=self._calendar_name,
            ):
                continue
            if most_recent_labelable is None:
                most_recent_labelable = row.as_of_trading_date
            if row.id is not None and row.id not in labeled_assessment_ids:
                unlabeled_label_ready_count += 1
                if most_recent_unlabeled_labelable is None:
                    most_recent_unlabeled_labelable = row.as_of_trading_date
        return (
            block_reason is None,
            block_reason,
            most_recent_labelable,
            most_recent_unlabeled_labelable,
            unlabeled_label_ready_count,
            forward_bar_shortfall,
            required_label_end_date,
            last_available_label_bar_date,
            min_horizon_forward_bar_shortfall,
            min_horizon_required_label_end_date,
            calendar_lag,
        )

    async def assessment_ids_with_labels(
        self,
        symbol: str,
        assessment_ids: list[int],
        *,
        label_method_id: str = LABEL_METHOD_ID,
    ) -> set[int]:
        """Return assessment ids that already have a label for ``label_method_id``."""

        return await self._label_store.assessment_ids_with_labels(
            symbol,
            assessment_ids,
            label_method_id=label_method_id,
        )

    async def select_backfill_candidates(
        self,
        symbol: str,
        snapshots_newest_first: list[ResearchAssessmentSnapshotData],
        limit: int,
    ) -> list[tuple[str, int]]:
        """Prefer unlabeled, label-ready assessments for Phase 49 backfill (ADR-0050)."""

        from aegis.domain.research_outcome_label_backfill import (
            select_label_backfill_candidates,
        )

        ids = [snapshot.id for snapshot in snapshots_newest_first if snapshot.id is not None]
        labeled_ids = await self.assessment_ids_with_labels(symbol, ids)
        bars = await self._bar_reader.list_recent_bars(symbol.upper(), self._bar_load_limit)
        return select_label_backfill_candidates(
            snapshots_newest_first,
            labeled_assessment_ids=labeled_ids,
            limit=limit,
            bars_newest_first=bars,
            calendar_name=self._calendar_name,
        )

    async def select_ready_horizons_backfill_candidates(
        self,
        symbol: str,
        snapshots_newest_first: list[ResearchAssessmentSnapshotData],
        limit: int,
    ) -> list[tuple[str, int]]:
        """Prefer unlabeled assessments with any ready horizon (ADR-0312)."""

        from aegis.domain.research_outcome_label_backfill import (
            select_ready_horizons_backfill_candidates,
        )

        ids = [snapshot.id for snapshot in snapshots_newest_first if snapshot.id is not None]
        labeled_ids = await self.assessment_ids_with_labels(symbol, ids)
        bars = await self._bar_reader.list_recent_bars(symbol.upper(), self._bar_load_limit)
        return select_ready_horizons_backfill_candidates(
            snapshots_newest_first,
            labeled_assessment_ids=labeled_ids,
            limit=limit,
            bars_newest_first=bars,
            calendar_name=self._calendar_name,
        )

    async def latest_label_for_assessment(
        self, assessment_snapshot_id: int
    ) -> OutcomeLabelData | None:
        return await self._label_store.get_latest_for_assessment(assessment_snapshot_id)

    async def list_labels_for_assessment(
        self,
        symbol: str,
        assessment_snapshot_id: int,
        limit: int,
    ) -> list[OutcomeLabelData]:
        """Return up to ``limit`` labels for ``assessment_snapshot_id`` and ``symbol``."""

        return await self._label_store.list_for_assessment(
            assessment_snapshot_id,
            limit,
            symbol=symbol,
        )


class ResearchAssessmentStoreForLabels(Protocol):
    async def get_by_id(
        self, assessment_snapshot_id: int
    ) -> ResearchAssessmentSnapshotData | None: ...


class ResearchBarReaderForLabels(Protocol):
    async def list_recent_bars(self, symbol: str, limit: int) -> list[ResearchBarInput]: ...
