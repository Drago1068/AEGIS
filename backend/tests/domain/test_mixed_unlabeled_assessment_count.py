"""Domain tests for mixed unlabeled assessment counting (Phase 67)."""

from __future__ import annotations

from datetime import UTC, date, datetime

from aegis.domain.research_assessment import (
    METHOD_ID,
    STATE_RESEARCH_ONLY,
    ResearchAssessmentSnapshotData,
    count_mixed_unlabeled_assessments,
)


def _snapshot(
    *,
    snapshot_id: int,
    component_source: str | None = None,
    input_source: str = "alpha_vantage",
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
        as_of_trading_date=date(2024, 1, 26),
        event_time=datetime(2024, 1, 26, 23, 59, 59, tzinfo=UTC),
        computed_at=datetime(2024, 1, 26, 18, 0, tzinfo=UTC),
        coverage_confidence=0.95,
        probability_confidence=None,
        components=components,
        schema_version=1,
        input_source=input_source,
        lookback_start_date=date(2023, 12, 27),
        lookback_end_date=date(2024, 1, 26),
        bar_count=20,
    )


def test_count_mixed_unlabeled_ignores_uniform_and_labeled() -> None:
    rows = [
        _snapshot(snapshot_id=3, component_source="mixed", input_source="mixed"),
        _snapshot(snapshot_id=2, component_source="mixed", input_source="mixed"),
        _snapshot(snapshot_id=1),
    ]
    assert count_mixed_unlabeled_assessments(rows, labeled_assessment_ids={2}) == 1


def test_count_mixed_unlabeled_zero_when_none_mixed() -> None:
    rows = [_snapshot(snapshot_id=1), _snapshot(snapshot_id=2, component_source="polygon")]
    assert count_mixed_unlabeled_assessments(rows, labeled_assessment_ids=set()) == 0
