"""Domain tests for historical research assessment backfill (Phase 45/47)."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from aegis.domain.research_assessment import (
    LOOKBACK_SESSIONS,
    ResearchAssessmentSnapshotData,
    ResearchBarInput,
)
from aegis.domain.research_assessment_backfill import (
    DEFAULT_MIN_FORWARD_SESSIONS,
    REASON_ALREADY_EXISTS,
    bars_as_of,
    candidate_as_of_dates,
    run_assessment_backfill,
)
from aegis.domain.research_outcome_labels import (
    FORWARD_HORIZON_SESSIONS,
    compute_forward_total_return_labels,
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


def _closes_to_bars(
    closes: list[Decimal],
    *,
    end_date: date,
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
        _bar(session_dates[i], close=str(closes[i])) for i in range(len(closes))
    ]
    return list(reversed(bars_chrono))


def test_bars_as_of_truncates_future_sessions() -> None:
    bars = [
        _bar(date(2024, 1, 26)),
        _bar(date(2024, 1, 25)),
        _bar(date(2024, 1, 24)),
    ]
    truncated = bars_as_of(bars, date(2024, 1, 25))
    assert [bar.trading_date for bar in truncated] == [
        date(2024, 1, 25),
        date(2024, 1, 24),
    ]


def test_candidate_as_of_dates_excludes_tip_without_forward_bars() -> None:
    """Tip dates lack 20 forward sessions; only older dates with coverage qualify."""

    n = LOOKBACK_SESSIONS + DEFAULT_MIN_FORWARD_SESSIONS + 3
    closes = [Decimal(str(100 + i)) for i in range(n)]
    bars = _closes_to_bars(closes, end_date=date(2024, 1, 26))
    tip = bars[0].trading_date
    candidates = candidate_as_of_dates(
        bars,
        limit=3,
        calendar_name=_CALENDAR,
    )
    assert tip not in candidates
    assert len(candidates) == 3
    assert candidates == sorted(candidates, reverse=True)
    # Newest eligible sits DEFAULT_MIN_FORWARD_SESSIONS behind the tip.
    chrono = list(reversed(bars))
    expected_newest_eligible = chrono[-(DEFAULT_MIN_FORWARD_SESSIONS + 1)].trading_date
    assert candidates[0] == expected_newest_eligible


def test_candidate_as_of_dates_skips_non_primary() -> None:
    n = LOOKBACK_SESSIONS + DEFAULT_MIN_FORWARD_SESSIONS + 2
    closes = [Decimal(str(100 + i)) for i in range(n)]
    bars = _closes_to_bars(closes, end_date=date(2024, 1, 26))
    chrono = list(reversed(bars))
    eligible = chrono[-(DEFAULT_MIN_FORWARD_SESSIONS + 1)]
    # Replace eligible primary with adjusted — should fall out of candidates.
    bars_mutated = [
        (
            ResearchBarInput(
                trading_date=bar.trading_date,
                open=bar.open,
                high=bar.high,
                low=bar.low,
                close=bar.close,
                volume=bar.volume,
                source="polygon",
                data_quality="adjusted",
            )
            if bar.trading_date == eligible.trading_date
            else bar
        )
        for bar in bars
    ]
    candidates = candidate_as_of_dates(
        bars_mutated,
        limit=5,
        calendar_name=_CALENDAR,
    )
    assert eligible.trading_date not in candidates


@pytest.mark.asyncio
async def test_run_assessment_backfill_persists_label_ready_and_skips_existing() -> None:
    n = LOOKBACK_SESSIONS + DEFAULT_MIN_FORWARD_SESSIONS + 5
    closes = [Decimal(str(100 + i)) for i in range(n)]
    bars = _closes_to_bars(closes, end_date=date(2024, 1, 26))
    chrono = list(reversed(bars))
    newest_eligible = chrono[-(DEFAULT_MIN_FORWARD_SESSIONS + 1)].trading_date
    existing = {newest_eligible}
    inserted: list[ResearchAssessmentSnapshotData] = []

    async def _insert(
        snapshot: ResearchAssessmentSnapshotData,
    ) -> ResearchAssessmentSnapshotData:
        with_id = replace(snapshot, id=len(inserted) + 1)
        inserted.append(with_id)
        return with_id

    summary = await run_assessment_backfill(
        "AAPL",
        bars_newest_first=bars,
        existing_as_of_dates=existing,
        limit=2,
        calendar_name=_CALENDAR,
        max_latest_bar_staleness_trading_days=5,
        insert_snapshot=_insert,
    )

    assert summary.candidate_count == 2
    assert summary.outcomes[0].as_of_trading_date == newest_eligible
    assert summary.outcomes[0].persisted is False
    assert summary.outcomes[0].reason == REASON_ALREADY_EXISTS
    assert summary.persisted_count == 1
    assert summary.skipped_count == 1
    assert len(inserted) == 1
    assert inserted[0].probability_confidence is None
    assert inserted[0].as_of_trading_date < newest_eligible

    # Persisted as-of must support Phase 13 labeling against the full series.
    label = compute_forward_total_return_labels(
        inserted[0],
        bars,
        calendar_name=_CALENDAR,
        horizons=FORWARD_HORIZON_SESSIONS,
    )
    assert "forward_return_5" in label.labels
    assert "forward_return_20" in label.labels


@pytest.mark.asyncio
async def test_run_assessment_backfill_no_label_ready_candidates() -> None:
    bars = [_bar(date(2024, 1, 26)), _bar(date(2024, 1, 25))]

    async def _insert(
        snapshot: ResearchAssessmentSnapshotData,
    ) -> ResearchAssessmentSnapshotData:
        raise AssertionError("must not insert")

    summary = await run_assessment_backfill(
        "AAPL",
        bars_newest_first=bars,
        existing_as_of_dates=set(),
        limit=1,
        calendar_name=_CALENDAR,
        max_latest_bar_staleness_trading_days=5,
        insert_snapshot=_insert,
    )
    assert summary.candidate_count == 0
    assert summary.persisted_count == 0
    assert summary.skipped_count == 0
