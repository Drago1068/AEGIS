"""Research assessment outcome labels (Phase 13, ADR-0014).

Framework-free forward-return label computation from stored daily bars. Outcomes are evidence
for a future calibration phase; they are not probabilities, recommendations, or trade signals.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import Protocol

from aegis.domain.calendars import is_trading_day
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

    bar_source = _resolve_label_bar_source(snapshot)
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


def _resolve_label_bar_source(snapshot: ResearchAssessmentSnapshotData) -> str:
    if snapshot.input_source != COMPONENT_SOURCE_MIXED:
        return snapshot.input_source
    component_source = snapshot.components.get("component_source")
    if isinstance(component_source, str) and component_source != COMPONENT_SOURCE_MIXED:
        return component_source
    return snapshot.input_source


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
