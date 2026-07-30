"""Domain tests for assessment component_source filtering (Phase 61)."""

from __future__ import annotations

from datetime import UTC, date, datetime

from aegis.domain.research_assessment import (
    METHOD_ID,
    STATE_RESEARCH_ONLY,
    ResearchAssessmentSnapshotData,
    filter_assessments_by_component_source,
)


def _snapshot(
    *,
    snapshot_id: int,
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


def test_filter_none_returns_limit_prefix() -> None:
    rows = [
        _snapshot(snapshot_id=3, component_source="mixed"),
        _snapshot(snapshot_id=2, component_source="polygon"),
        _snapshot(snapshot_id=1),
    ]
    assert [
        row.id for row in filter_assessments_by_component_source(rows, None, limit=2)
    ] == [3, 2]


def test_filter_mixed_only() -> None:
    rows = [
        _snapshot(snapshot_id=3, component_source="polygon"),
        _snapshot(snapshot_id=2, component_source="mixed"),
        _snapshot(snapshot_id=1, input_source="mixed", component_source="mixed"),
    ]
    matched = filter_assessments_by_component_source(rows, "mixed", limit=10)
    assert [row.id for row in matched] == [2, 1]


def test_filter_exact_source_and_limit() -> None:
    rows = [
        _snapshot(snapshot_id=4, component_source="polygon"),
        _snapshot(snapshot_id=3, component_source="mixed"),
        _snapshot(snapshot_id=2, component_source="polygon"),
        _snapshot(snapshot_id=1),
    ]
    matched = filter_assessments_by_component_source(rows, "polygon", limit=1)
    assert [row.id for row in matched] == [4]
