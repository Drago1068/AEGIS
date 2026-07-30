"""Domain tests for historical research assessment backfill (Phase 45)."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from aegis.domain.research_assessment import (
    LOOKBACK_SESSIONS,
    ResearchAssessmentReason,
    ResearchAssessmentSnapshotData,
    ResearchBarInput,
)
from aegis.domain.research_assessment_backfill import (
    REASON_ALREADY_EXISTS,
    bars_as_of,
    candidate_as_of_dates,
    run_assessment_backfill,
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


def test_candidate_as_of_dates_newest_primary_first() -> None:
    bars = [
        _bar(date(2024, 1, 26)),
        ResearchBarInput(
            trading_date=date(2024, 1, 25),
            open=Decimal("1"),
            high=Decimal("1"),
            low=Decimal("1"),
            close=Decimal("1"),
            volume=1,
            source="polygon",
            data_quality="adjusted",
        ),
        _bar(date(2024, 1, 24)),
    ]
    assert candidate_as_of_dates(bars, limit=2) == [
        date(2024, 1, 26),
        date(2024, 1, 24),
    ]


@pytest.mark.asyncio
async def test_run_assessment_backfill_persists_and_skips_existing() -> None:
    closes = [Decimal(str(100 + i)) for i in range(LOOKBACK_SESSIONS + 5)]
    bars = _closes_to_bars(closes, end_date=date(2024, 1, 26))
    # Newest primary date already assessed.
    newest = bars[0].trading_date
    existing = {newest}
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
    assert summary.outcomes[0].as_of_trading_date == newest
    assert summary.outcomes[0].persisted is False
    assert summary.outcomes[0].reason == REASON_ALREADY_EXISTS
    assert summary.persisted_count == 1
    assert summary.skipped_count == 1
    assert len(inserted) == 1
    assert inserted[0].probability_confidence is None
    assert inserted[0].as_of_trading_date < newest


@pytest.mark.asyncio
async def test_run_assessment_backfill_insufficient_lookback_fail_closed() -> None:
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
    assert summary.persisted_count == 0
    assert summary.skipped_count == 1
    assert (
        summary.outcomes[0].reason
        == ResearchAssessmentReason.INSUFFICIENT_PRIMARY_BARS.value
    )
