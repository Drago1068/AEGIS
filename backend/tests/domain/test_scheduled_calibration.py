"""Unit tests for post-assessment calibration orchestration (Phase 15)."""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from aegis.domain.research_assessment import (
    METHOD_ID,
    STATE_RESEARCH_ONLY,
    ResearchAssessmentSnapshotData,
)
from aegis.domain.research_probability_calibration import (
    CalibrationReason,
    CalibrationUnavailableError,
)
from aegis.domain.scheduled_calibration import (
    run_calibrations_after_assessments,
    run_calibrations_after_labels,
    try_calibrate_assessment_after_create,
)
from aegis.domain.scheduled_outcome_labels import (
    OutcomeLabelAfterAssessmentOutcome,
    OutcomeLabelAfterAssessmentSummary,
)


def _snapshot() -> ResearchAssessmentSnapshotData:
    return ResearchAssessmentSnapshotData(
        id=42,
        symbol="AAPL",
        method_id=METHOD_ID,
        method_version=1,
        state=STATE_RESEARCH_ONLY,
        as_of_trading_date=date(2024, 1, 26),
        event_time=datetime(2024, 1, 26, 23, 59, 59, tzinfo=UTC),
        computed_at=datetime(2024, 1, 26, 18, 0, tzinfo=UTC),
        coverage_confidence=0.9,
        probability_confidence=None,
        components={"research_index": 0.46},
        schema_version=1,
        input_source="alpha_vantage",
        lookback_start_date=date(2023, 12, 27),
        lookback_end_date=date(2024, 1, 26),
        bar_count=20,
    )


class FakeCalibrationService:
    def __init__(self, *, fail_ids: dict[int, Exception] | None = None) -> None:
        self.fail_ids = fail_ids or {}
        self.calls: list[tuple[str, int]] = []

    async def calibrate_assessment(self, symbol: str, assessment_snapshot_id: int) -> object:
        self.calls.append((symbol, assessment_snapshot_id))
        if assessment_snapshot_id in self.fail_ids:
            raise self.fail_ids[assessment_snapshot_id]
        return {"id": 1}


@pytest.mark.asyncio
async def test_run_calibrations_after_assessments_persists() -> None:
    service = FakeCalibrationService()

    summary = await run_calibrations_after_assessments([("aapl", 1), ("MSFT", 2)], service)

    assert service.calls == [("AAPL", 1), ("MSFT", 2)]
    assert summary.persisted_count == 2


@pytest.mark.asyncio
async def test_run_calibrations_after_labels_uses_persisted_only() -> None:
    service = FakeCalibrationService()
    label_summary = OutcomeLabelAfterAssessmentSummary(
        outcomes=(
            OutcomeLabelAfterAssessmentOutcome(
                symbol="AAPL",
                assessment_snapshot_id=10,
                persisted=True,
            ),
            OutcomeLabelAfterAssessmentOutcome(
                symbol="MSFT",
                assessment_snapshot_id=11,
                persisted=False,
                reason="insufficient_forward_bars",
            ),
        )
    )

    summary = await run_calibrations_after_labels(label_summary, service)

    assert service.calls == [("AAPL", 10)]
    assert summary.persisted_count == 1


@pytest.mark.asyncio
async def test_try_calibrate_swallows_fail_closed() -> None:
    service = FakeCalibrationService(
        fail_ids={
            42: CalibrationUnavailableError(
                CalibrationReason.INSUFFICIENT_LABELED_CORPUS,
                "thin",
            )
        }
    )

    await try_calibrate_assessment_after_create(_snapshot(), service)

    assert service.calls == [("AAPL", 42)]
