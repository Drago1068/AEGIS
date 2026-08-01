"""Domain tests for outcome-label backfill candidate selection (Phase 49 / 57)."""

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
    select_ready_horizons_backfill_candidates,
)
from aegis.domain.research_outcome_labels import is_snapshot_label_ready, ready_forward_horizons

_CALENDAR = "NYSE"


def _bar(
    trading_date: date,
    *,
    close: str = "100",
    source: str = "alpha_vantage",
) -> ResearchBarInput:
    value = Decimal(close)
    return ResearchBarInput(
        trading_date=trading_date,
        open=value,
        high=value,
        low=value,
        close=value,
        volume=1_000,
        source=source,
        data_quality="primary",
    )


def _closes_to_bars(
    closes: list[Decimal],
    *,
    end_date: date,
    source: str = "alpha_vantage",
) -> list[ResearchBarInput]:
    from aegis.domain.calendars import is_trading_day

    session_dates: list[date] = []
    cursor = end_date
    while len(session_dates) < len(closes):
        if is_trading_day(cursor, _CALENDAR):
            session_dates.append(cursor)
        cursor = date.fromordinal(cursor.toordinal() - 1)
    session_dates.reverse()
    bars_chrono = [
        _bar(session_dates[i], close=str(closes[i]), source=source)
        for i in range(len(closes))
    ]
    return list(reversed(bars_chrono))


def _snapshot(
    *,
    snapshot_id: int,
    as_of: date,
    input_source: str = "alpha_vantage",
    component_source: str | None = None,
) -> ResearchAssessmentSnapshotData:
    components: dict[str, float | str] = {"research_index": 0.46}
    if component_source is not None:
        components["component_source"] = component_source
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
        components=components,
        schema_version=1,
        input_source=input_source,
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
    pairs = select_label_backfill_candidates(
        snapshots,
        labeled_assessment_ids={2},
        limit=5,
        bars_newest_first=bars,
        calendar_name=_CALENDAR,
    )
    assert pairs == [("AAPL", 3)]


def test_select_ready_horizons_includes_min_ready_when_full_blocked() -> None:
    """Min-horizon-ready as-of is eligible even when max horizon is still short."""

    # Enough bars for 5-session horizon but not 20.
    n = LOOKBACK_SESSIONS + 5 + 2
    closes = [Decimal(str(100 + i)) for i in range(n)]
    bars = _closes_to_bars(closes, end_date=date(2024, 1, 26))
    tip = bars[0].trading_date
    chrono = list(reversed(bars))
    min_ready_as_of = chrono[-(5 + 1)].trading_date

    tip_snap = _snapshot(snapshot_id=1, as_of=tip)
    min_snap = _snapshot(snapshot_id=2, as_of=min_ready_as_of)
    assert ready_forward_horizons(tip_snap, bars, calendar_name=_CALENDAR) == ()
    assert ready_forward_horizons(min_snap, bars, calendar_name=_CALENDAR) == (5,)
    assert not is_snapshot_label_ready(min_snap, bars, calendar_name=_CALENDAR)

    pairs = select_ready_horizons_backfill_candidates(
        [tip_snap, min_snap],
        labeled_assessment_ids=set(),
        limit=5,
        bars_newest_first=bars,
        calendar_name=_CALENDAR,
    )
    assert pairs == [("AAPL", 2)]
    full_pairs = select_label_backfill_candidates(
        [tip_snap, min_snap],
        labeled_assessment_ids=set(),
        limit=5,
        bars_newest_first=bars,
        calendar_name=_CALENDAR,
    )
    assert full_pairs == []


def test_select_ready_horizons_excludes_labeled() -> None:
    n = LOOKBACK_SESSIONS + 5 + 2
    closes = [Decimal(str(100 + i)) for i in range(n)]
    bars = _closes_to_bars(closes, end_date=date(2024, 1, 26))
    chrono = list(reversed(bars))
    min_ready_as_of = chrono[-(5 + 1)].trading_date
    snap = _snapshot(snapshot_id=9, as_of=min_ready_as_of)
    pairs = select_ready_horizons_backfill_candidates(
        [snap],
        labeled_assessment_ids={9},
        limit=5,
        bars_newest_first=bars,
        calendar_name=_CALENDAR,
    )
    assert pairs == []


def test_select_full_backfill_includes_partial_when_complete_ids_empty() -> None:
    """Partial-labeled ids are eligible when callers pass only complete-horizon ids."""

    n = LOOKBACK_SESSIONS + DEFAULT_MIN_FORWARD_SESSIONS + 3
    closes = [Decimal(str(100 + i)) for i in range(n)]
    bars = _closes_to_bars(closes, end_date=date(2024, 1, 26))
    chrono = list(reversed(bars))
    ready_as_of = chrono[-(DEFAULT_MIN_FORWARD_SESSIONS + 1)].trading_date
    snap = _snapshot(snapshot_id=11, as_of=ready_as_of)
    # Treat as incomplete (not in complete_ids) even though "labeled" partially.
    pairs = select_label_backfill_candidates(
        [snap],
        labeled_assessment_ids=set(),
        limit=5,
        bars_newest_first=bars,
        calendar_name=_CALENDAR,
    )
    assert pairs == [("AAPL", 11)]
    pairs_complete = select_label_backfill_candidates(
        [snap],
        labeled_assessment_ids={11},
        limit=5,
        bars_newest_first=bars,
        calendar_name=_CALENDAR,
    )
    assert pairs_complete == []


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
        bars_newest_first=bars,
        calendar_name=_CALENDAR,
    )
    assert pairs == [("AAPL", 4)]


def test_source_aware_ready_omits_when_only_other_source_has_forward() -> None:
    """AV-primary assessment is not ready if only Polygon has the forward close."""

    n = LOOKBACK_SESSIONS + DEFAULT_MIN_FORWARD_SESSIONS + 3
    closes = [Decimal(str(100 + i)) for i in range(n)]
    av_bars = _closes_to_bars(closes, end_date=date(2024, 1, 26), source="alpha_vantage")
    chrono = list(reversed(av_bars))
    ready_as_of = chrono[-(DEFAULT_MIN_FORWARD_SESSIONS + 1)].trading_date

    # Drop AV bars after ready_as_of so AV lacks forward horizon; keep Polygon full.
    av_truncated = [
        bar
        for bar in av_bars
        if bar.trading_date <= ready_as_of
    ]
    poly_full = _closes_to_bars(closes, end_date=date(2024, 1, 26), source="polygon")
    mixed_bars = av_truncated + poly_full

    snapshot = _snapshot(snapshot_id=7, as_of=ready_as_of, input_source="alpha_vantage")
    assert not is_snapshot_label_ready(snapshot, mixed_bars, calendar_name=_CALENDAR)

    # Any-source date set would still mark ready_as_of (false ready).
    any_ready = label_ready_as_of_dates(mixed_bars, calendar_name=_CALENDAR)
    assert ready_as_of in any_ready

    pairs = select_label_backfill_candidates(
        [snapshot],
        labeled_assessment_ids=set(),
        limit=5,
        bars_newest_first=mixed_bars,
        calendar_name=_CALENDAR,
    )
    assert pairs == []


def test_source_aware_ready_uses_component_source_when_input_mixed() -> None:
    n = LOOKBACK_SESSIONS + DEFAULT_MIN_FORWARD_SESSIONS + 3
    closes = [Decimal(str(100 + i)) for i in range(n)]
    poly_bars = _closes_to_bars(closes, end_date=date(2024, 1, 26), source="polygon")
    chrono = list(reversed(poly_bars))
    ready_as_of = chrono[-(DEFAULT_MIN_FORWARD_SESSIONS + 1)].trading_date
    snapshot = _snapshot(
        snapshot_id=8,
        as_of=ready_as_of,
        input_source="mixed",
        component_source="polygon",
    )
    assert is_snapshot_label_ready(snapshot, poly_bars, calendar_name=_CALENDAR)
    pairs = select_label_backfill_candidates(
        [snapshot],
        labeled_assessment_ids=set(),
        limit=1,
        bars_newest_first=poly_bars,
        calendar_name=_CALENDAR,
    )
    assert pairs == [("AAPL", 8)]


def test_select_prefers_mixed_before_uniform_newest() -> None:
    """Phase 65: mixed unlabeled ready candidates precede newer uniform-source peers."""

    n = LOOKBACK_SESSIONS + DEFAULT_MIN_FORWARD_SESSIONS + 4
    closes = [Decimal(str(100 + i)) for i in range(n)]
    bars = _closes_to_bars(closes, end_date=date(2024, 1, 26))
    chrono = list(reversed(bars))
    ready_newest = chrono[-(DEFAULT_MIN_FORWARD_SESSIONS + 1)].trading_date
    ready_older = chrono[-(DEFAULT_MIN_FORWARD_SESSIONS + 2)].trading_date
    snapshots = [
        _snapshot(snapshot_id=5, as_of=ready_newest),
        _snapshot(
            snapshot_id=4,
            as_of=ready_older,
            input_source="mixed",
            component_source="mixed",
        ),
    ]
    # Older mixed row needs AV bars on as_of (coverage prefers alpha_vantage).
    snapshots[1].components["coverage_sources"] = ["alpha_vantage", "polygon"]
    pairs = select_label_backfill_candidates(
        snapshots,
        labeled_assessment_ids=set(),
        limit=1,
        bars_newest_first=bars,
        calendar_name=_CALENDAR,
    )
    assert pairs == [("AAPL", 4)]


def test_true_mixed_ready_resolves_as_of_source_from_coverage() -> None:
    n = LOOKBACK_SESSIONS + DEFAULT_MIN_FORWARD_SESSIONS + 3
    closes = [Decimal(str(100 + i)) for i in range(n)]
    av_bars = _closes_to_bars(closes, end_date=date(2024, 1, 26), source="alpha_vantage")
    chrono = list(reversed(av_bars))
    ready_as_of = chrono[-(DEFAULT_MIN_FORWARD_SESSIONS + 1)].trading_date
    snapshot = _snapshot(
        snapshot_id=9,
        as_of=ready_as_of,
        input_source="mixed",
        component_source="mixed",
    )
    snapshot.components["coverage_sources"] = ["alpha_vantage", "polygon"]
    assert is_snapshot_label_ready(snapshot, av_bars, calendar_name=_CALENDAR)
    pairs = select_label_backfill_candidates(
        [snapshot],
        labeled_assessment_ids=set(),
        limit=1,
        bars_newest_first=av_bars,
        calendar_name=_CALENDAR,
    )
    assert pairs == [("AAPL", 9)]
