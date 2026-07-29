"""Unit tests for post-ingest research orchestration (Phase 8)."""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from aegis.domain.research_assessment import (
    METHOD_ID,
    STATE_RESEARCH_ONLY,
    ResearchAssessmentReason,
    ResearchAssessmentSnapshotData,
    ResearchAssessmentUnavailableError,
)
from aegis.domain.scheduled_research import run_research_after_ingest


def _snapshot(symbol: str = "AAPL") -> ResearchAssessmentSnapshotData:
    return ResearchAssessmentSnapshotData(
        id=1,
        symbol=symbol,
        method_id=METHOD_ID,
        method_version=1,
        state=STATE_RESEARCH_ONLY,
        as_of_trading_date=date(2024, 1, 26),
        event_time=datetime(2024, 1, 26, 23, 59, 59, tzinfo=UTC),
        computed_at=datetime(2024, 1, 26, 18, 0, tzinfo=UTC),
        coverage_confidence=0.95,
        probability_confidence=None,
        components={
            "total_return_20": 0.1,
            "realized_vol_20": 0.2,
            "research_index": 0.46,
        },
        schema_version=1,
        input_source="alpha_vantage",
        lookback_start_date=date(2023, 12, 27),
        lookback_end_date=date(2024, 1, 26),
        bar_count=20,
    )


class FakeResearchService:
    def __init__(
        self,
        *,
        fail_symbols: dict[str, Exception] | None = None,
    ) -> None:
        self.fail_symbols = fail_symbols or {}
        self.assess_calls: list[str] = []

    async def assess(self, symbol: str) -> ResearchAssessmentSnapshotData:
        self.assess_calls.append(symbol)
        if symbol in self.fail_symbols:
            raise self.fail_symbols[symbol]
        return _snapshot(symbol)


@pytest.mark.asyncio
async def test_run_research_after_ingest_persists_per_symbol() -> None:
    service = FakeResearchService()

    summary = await run_research_after_ingest(["aapl", "MSFT"], service)

    assert service.assess_calls == ["AAPL", "MSFT"]
    assert summary.persisted_count == 2
    assert summary.skipped_count == 0
    assert all(outcome.persisted for outcome in summary.outcomes)
    assert all(outcome.reason is None for outcome in summary.outcomes)
    assert all(outcome.assessment_snapshot_id == 1 for outcome in summary.outcomes)


@pytest.mark.asyncio
async def test_run_research_after_ingest_skips_fail_closed_without_aborting() -> None:
    service = FakeResearchService(
        fail_symbols={
            "MSFT": ResearchAssessmentUnavailableError(
                ResearchAssessmentReason.INSUFFICIENT_PRIMARY_BARS,
                "need 20 usable primary bars, found 3",
            )
        }
    )

    summary = await run_research_after_ingest(["AAPL", "MSFT", "SPY"], service)

    assert service.assess_calls == ["AAPL", "MSFT", "SPY"]
    assert summary.persisted_count == 2
    assert summary.skipped_count == 1
    skipped = next(outcome for outcome in summary.outcomes if outcome.symbol == "MSFT")
    assert skipped.persisted is False
    assert skipped.reason == "insufficient_primary_bars"


@pytest.mark.asyncio
async def test_run_research_after_ingest_treats_unexpected_errors_as_skip() -> None:
    service = FakeResearchService(fail_symbols={"AAPL": RuntimeError("boom")})

    summary = await run_research_after_ingest(["AAPL", "MSFT"], service)

    assert summary.persisted_count == 1
    assert summary.skipped_count == 1
    skipped = summary.outcomes[0]
    assert skipped.symbol == "AAPL"
    assert skipped.reason == "unexpected_error"
