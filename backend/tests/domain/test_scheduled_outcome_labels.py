"""Unit tests for post-assessment outcome label orchestration (Phase 14)."""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from aegis.domain.research_assessment import (
    METHOD_ID,
    STATE_RESEARCH_ONLY,
    ResearchAssessmentSnapshotData,
)
from aegis.domain.research_outcome_labels import (
    OutcomeLabelReason,
    OutcomeLabelUnavailableError,
)
from aegis.domain.scheduled_outcome_labels import (
    run_outcome_labels_after_assessments,
    run_outcome_labels_after_research,
    try_label_assessment_after_create,
)
from aegis.domain.scheduled_research import (
    ResearchAfterIngestSummary,
    ResearchAfterIngestSymbolOutcome,
)


def _snapshot(*, snapshot_id: int = 42) -> ResearchAssessmentSnapshotData:
    return ResearchAssessmentSnapshotData(
        id=snapshot_id,
        symbol="AAPL",
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


class FakeOutcomeLabelService:
    def __init__(
        self,
        *,
        fail_ids: dict[int, Exception] | None = None,
    ) -> None:
        self.fail_ids = fail_ids or {}
        self.label_calls: list[tuple[str, int]] = []

    async def label_assessment(self, symbol: str, assessment_snapshot_id: int) -> object:
        self.label_calls.append((symbol, assessment_snapshot_id))
        if assessment_snapshot_id in self.fail_ids:
            raise self.fail_ids[assessment_snapshot_id]
        return {"id": 1}


@pytest.mark.asyncio
async def test_run_outcome_labels_after_assessments_persists_per_assessment() -> None:
    service = FakeOutcomeLabelService()

    summary = await run_outcome_labels_after_assessments(
        [("aapl", 1), ("MSFT", 2)],
        service,
    )

    assert service.label_calls == [("AAPL", 1), ("MSFT", 2)]
    assert summary.persisted_count == 2
    assert summary.skipped_count == 0


@pytest.mark.asyncio
async def test_run_outcome_labels_skips_fail_closed_without_aborting() -> None:
    service = FakeOutcomeLabelService(
        fail_ids={
            2: OutcomeLabelUnavailableError(
                OutcomeLabelReason.INSUFFICIENT_FORWARD_BARS,
                "need close on horizon end",
            )
        }
    )

    summary = await run_outcome_labels_after_assessments(
        [("AAPL", 1), ("MSFT", 2), ("SPY", 3)],
        service,
    )

    assert summary.persisted_count == 2
    assert summary.skipped_count == 1
    skipped = next(outcome for outcome in summary.outcomes if outcome.assessment_snapshot_id == 2)
    assert skipped.reason == "insufficient_forward_bars"


@pytest.mark.asyncio
async def test_run_outcome_labels_after_research_uses_persisted_ids_only() -> None:
    service = FakeOutcomeLabelService()
    research_summary = ResearchAfterIngestSummary(
        outcomes=(
            ResearchAfterIngestSymbolOutcome(
                symbol="AAPL",
                persisted=True,
                assessment_snapshot_id=10,
            ),
            ResearchAfterIngestSymbolOutcome(
                symbol="MSFT",
                persisted=False,
                reason="stale_latest_bar",
            ),
        )
    )

    summary = await run_outcome_labels_after_research(research_summary, service)

    assert service.label_calls == [("AAPL", 10)]
    assert summary.persisted_count == 1


@pytest.mark.asyncio
async def test_try_label_assessment_after_create_swallows_fail_closed() -> None:
    service = FakeOutcomeLabelService(
        fail_ids={
            42: OutcomeLabelUnavailableError(
                OutcomeLabelReason.INSUFFICIENT_FORWARD_BARS,
                "not enough bars",
            )
        }
    )

    await try_label_assessment_after_create(_snapshot(), service)

    assert service.label_calls == [("AAPL", 42)]


@pytest.mark.asyncio
async def test_try_label_assessment_after_create_skips_missing_id() -> None:
    service = FakeOutcomeLabelService()
    base = _snapshot(snapshot_id=42)
    snapshot = ResearchAssessmentSnapshotData(
        id=None,
        symbol=base.symbol,
        method_id=base.method_id,
        method_version=base.method_version,
        state=base.state,
        as_of_trading_date=base.as_of_trading_date,
        event_time=base.event_time,
        computed_at=base.computed_at,
        coverage_confidence=base.coverage_confidence,
        probability_confidence=base.probability_confidence,
        components=base.components,
        schema_version=base.schema_version,
        input_source=base.input_source,
        lookback_start_date=base.lookback_start_date,
        lookback_end_date=base.lookback_end_date,
        bar_count=base.bar_count,
    )

    await try_label_assessment_after_create(snapshot, service)

    assert service.label_calls == []
