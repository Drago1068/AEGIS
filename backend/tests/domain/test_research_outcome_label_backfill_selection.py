"""Domain tests for outcome-label backfill candidate selection (Phase 49)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from aegis.domain.research_assessment import (
    LOOKBACK_SESSIONS,
    METHOD_ID,
    STATE_RESEARCH_ONLY,
    ResearchAssessmentSnapshotData,
    ResearchBarInput,
)
from aegis.domain.research_assessment_backfill import DEFAULT_MIN_FORWARD_SESSIONS
from aegis.domain.research_outcome_label_backfill import (
    label_ready_as_of_dates,
    select_label_backfill_candidates,
)

_CALENDAR = "NYSE"


def _bar(trading_date: date, *, close: str = "100") -> ResearchBarInput:
    value = Decimal(close)
    return ResearchBarInput(
        trading_date=trading_date,
        open=value,
        high=value,
        low=value,
        close=value,
        volume=1_000,
        source="alpha_vantage",
        data_quality="primary",
    )


def _closes_to_bars(closes: list[Decimal], *, end_date: date) -> list[ResearchBarInput]:
    from aegis.domain.calendars import is_trading_day

    session_dates: list[date] = []
    cursor = end_date
    while len(session_dates) < len(closes):
        if is_trading_day(cursor, _CALENDAR):
            session_dates.append(cursor)
        cursor = date.fromordinal(cursor.toordinal() - 1)
    session_dates.reverse()
    bars_chrono = [
        _bar(session_dates[i], close=str(closes[i])) for i in range(len(closes))
    ]
    return list(reversed(bars_chrono))


def _snapshot(*, snapshot_id: int, as_of: date) -> ResearchAssessmentSnapshotData:
    return ResearchAssessmentSnapshotData(
        id=snapshot_id,
        symbol="AAPL",
        method_id=METHOD_ID,
        method_version=1,
        state=STATE_RESEARCH_ONLY,
        as_of_trading_date=as_of,
        event_time=datetime(2024, 1, 26, 23, 59, 59, tzinfo=UTC),
        computed_at=datetime(2024, 1, 26, 18, 0, tzinfo=UTC),
        coverage_confidence=0.95,
        probability_confidence=None,
        components={"research_index": 0.46},
        schema_version=1,
        input_source="alpha_vantage",
        lookback_start_date=date(2023, 12, 27),
        lookback_end_date=as_of,
        bar_count=20,
    )


def test_select_excludes_labeled_and_prefers_label_ready() -> None:
    n = LOOKBACK_SESSIONS + DEFAULT_MIN_FORWARD_SESSIONS + 5
    closes = [Decimal(str(100 + i)) for i in range(n)]
    bars = _closes_to_bars(closes, end_date=date(2024, 1, 26))
    tip = bars[0].trading_date
    chrono = list(reversed(bars))
    ready_as_of = chrono[-(DEFAULT_MIN_FORWARD_SESSIONS + 1)].trading_date
    older_ready = chrono[-(DEFAULT_MIN_FORWARD_SESSIONS + 2)].trading_date

    ready_dates = label_ready_as_of_dates(bars, calendar_name=_CALENDAR)
    assert tip not in ready_dates
    assert ready_as_of in ready_dates

    snapshots = [
        _snapshot(snapshot_id=1, as_of=tip),
        _snapshot(snapshot_id=2, as_of=ready_as_of),
        _snapshot(snapshot_id=3, as_of=older_ready),
    ]
    # id=2 already labeled — omit; tip not ready — omit; id=3 selected.
    pairs = select_label_backfill_candidates(
        snapshots,
        labeled_assessment_ids={2},
        limit=5,
        label_ready_as_of=ready_dates,
    )
    assert pairs == [("AAPL", 3)]


def test_select_unlabeled_without_ready_filter_keeps_tip() -> None:
    snapshots = [
        _snapshot(snapshot_id=10, as_of=date(2024, 1, 26)),
        _snapshot(snapshot_id=9, as_of=date(2024, 1, 25)),
    ]
    pairs = select_label_backfill_candidates(
        snapshots,
        labeled_assessment_ids={10},
        limit=1,
        label_ready_as_of=None,
    )
    assert pairs == [("AAPL", 9)]


def test_select_respects_limit_newest_first_among_ready() -> None:
    n = LOOKBACK_SESSIONS + DEFAULT_MIN_FORWARD_SESSIONS + 4
    closes = [Decimal(str(100 + i)) for i in range(n)]
    bars = _closes_to_bars(closes, end_date=date(2024, 1, 26))
    ready_dates = label_ready_as_of_dates(bars, calendar_name=_CALENDAR)
    chrono = list(reversed(bars))
    ready_newest = chrono[-(DEFAULT_MIN_FORWARD_SESSIONS + 1)].trading_date
    ready_older = chrono[-(DEFAULT_MIN_FORWARD_SESSIONS + 2)].trading_date
    snapshots = [
        _snapshot(snapshot_id=5, as_of=bars[0].trading_date),
        _snapshot(snapshot_id=4, as_of=ready_newest),
        _snapshot(snapshot_id=3, as_of=ready_older),
    ]
    pairs = select_label_backfill_candidates(
        snapshots,
        labeled_assessment_ids=set(),
        limit=1,
        label_ready_as_of=ready_dates,
    )
    assert pairs == [("AAPL", 4)]
