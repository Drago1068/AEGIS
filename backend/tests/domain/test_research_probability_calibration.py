"""Unit tests for research probability calibration (Phase 15)."""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from aegis.domain.research_assessment import (
    METHOD_ID,
    STATE_RESEARCH_ONLY,
    ResearchAssessmentSnapshotData,
)
from aegis.domain.research_probability_calibration import (
    CALIBRATION_METHOD_ID,
    CalibrationReadinessStatus,
    CalibrationReason,
    CalibrationUnavailableError,
    LabeledResearchExample,
    compute_research_calibration_v1,
    evaluate_calibration_readiness,
)


def _snapshot(**overrides: object) -> ResearchAssessmentSnapshotData:
    defaults: dict[str, object] = {
        "id": 100,
        "symbol": "AAPL",
        "method_id": METHOD_ID,
        "method_version": 2,
        "state": STATE_RESEARCH_ONLY,
        "as_of_trading_date": date(2024, 1, 26),
        "event_time": datetime(2024, 1, 26, 23, 59, 59, tzinfo=UTC),
        "computed_at": datetime(2024, 1, 26, 18, 0, tzinfo=UTC),
        "coverage_confidence": 0.9,
        "probability_confidence": None,
        "components": {
            "total_return_20": 0.1,
            "realized_vol_20": 0.2,
            "research_index": 0.46,
        },
        "schema_version": 2,
        "input_source": "alpha_vantage",
        "lookback_start_date": date(2023, 12, 27),
        "lookback_end_date": date(2024, 1, 26),
        "bar_count": 20,
    }
    defaults.update(overrides)
    return ResearchAssessmentSnapshotData(**defaults)  # type: ignore[arg-type]


def _corpus(count: int, *, research_index: float = 0.46) -> list[LabeledResearchExample]:
    return [
        LabeledResearchExample(
            assessment_snapshot_id=index,
            research_index=research_index,
            forward_return=0.01 if index % 2 == 0 else -0.01,
            outcome_horizon_key="forward_return_5",
        )
        for index in range(1, count + 1)
    ]


def test_compute_calibration_empirical_hit_rate() -> None:
    calibration = compute_research_calibration_v1(
        _snapshot(),
        _corpus(12),
        min_corpus=10,
        min_bucket=5,
        index_bucket_width=0.15,
    )

    assert calibration.calibration_method_id == CALIBRATION_METHOD_ID
    assert calibration.probability_confidence == 0.5
    assert calibration.corpus_count == 12
    assert calibration.bucket_count == 12


def test_compute_calibration_fail_closed_thin_corpus() -> None:
    with pytest.raises(CalibrationUnavailableError) as exc_info:
        compute_research_calibration_v1(
            _snapshot(),
            _corpus(5),
            min_corpus=10,
            min_bucket=5,
            index_bucket_width=0.15,
        )

    assert exc_info.value.reason == CalibrationReason.INSUFFICIENT_LABELED_CORPUS


def test_compute_calibration_fail_closed_thin_bucket() -> None:
    corpus = _corpus(12, research_index=0.1)
    with pytest.raises(CalibrationUnavailableError) as exc_info:
        compute_research_calibration_v1(
            _snapshot(),
            corpus,
            min_corpus=10,
            min_bucket=5,
            index_bucket_width=0.01,
        )

    assert exc_info.value.reason == CalibrationReason.INSUFFICIENT_SIMILAR_EXAMPLES


def test_evaluate_readiness_ready() -> None:
    readiness = evaluate_calibration_readiness(
        "aapl",
        _snapshot(),
        _corpus(12),
        min_corpus=10,
        min_bucket=5,
        index_bucket_width=0.15,
    )

    assert readiness.status == CalibrationReadinessStatus.READY
    assert readiness.symbol == "AAPL"
    assert readiness.corpus_count == 12
    assert readiness.bucket_count == 12
    assert readiness.research_index == pytest.approx(0.46)


def test_evaluate_readiness_no_assessment() -> None:
    readiness = evaluate_calibration_readiness(
        "MSFT",
        None,
        [],
        min_corpus=10,
        min_bucket=5,
        index_bucket_width=0.15,
    )

    assert readiness.status == CalibrationReadinessStatus.NO_ASSESSMENT
    assert readiness.symbol == "MSFT"


def test_evaluate_readiness_insufficient_corpus() -> None:
    readiness = evaluate_calibration_readiness(
        "AAPL",
        _snapshot(),
        _corpus(4),
        min_corpus=10,
        min_bucket=5,
        index_bucket_width=0.15,
    )

    assert readiness.status == CalibrationReadinessStatus.INSUFFICIENT_LABELED_CORPUS
    assert readiness.corpus_count == 4
