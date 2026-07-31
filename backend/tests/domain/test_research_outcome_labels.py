"""Unit tests for forward-return outcome label computation (ADR-0014)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from aegis.domain.research_assessment import (
    METHOD_ID,
    STATE_RESEARCH_ONLY,
    ResearchAssessmentSnapshotData,
    ResearchBarInput,
)
from aegis.domain.research_outcome_labels import (
    OutcomeLabelReason,
    OutcomeLabelUnavailableError,
    compute_forward_total_return_labels,
    forward_horizon_end_date,
    snapshot_forward_bar_shortfall,
    snapshot_required_label_end_date,
)

_AS_OF = date(2024, 1, 2)
_SOURCE = "alpha_vantage"


def _snapshot(**overrides: object) -> ResearchAssessmentSnapshotData:
    defaults: dict[str, object] = {
        "id": 1,
        "symbol": "AAPL",
        "method_id": METHOD_ID,
        "method_version": 2,
        "state": STATE_RESEARCH_ONLY,
        "as_of_trading_date": _AS_OF,
        "event_time": datetime(2024, 1, 2, 23, 59, 59, tzinfo=UTC),
        "computed_at": datetime(2024, 1, 2, 18, 0, tzinfo=UTC),
        "coverage_confidence": 0.9,
        "probability_confidence": None,
        "components": {"total_return_20": 0.1},
        "schema_version": 2,
        "input_source": _SOURCE,
        "lookback_start_date": date(2023, 12, 1),
        "lookback_end_date": _AS_OF,
        "bar_count": 20,
    }
    defaults.update(overrides)
    return ResearchAssessmentSnapshotData(**defaults)  # type: ignore[arg-type]


def _bar(trading_date: date, close: Decimal) -> ResearchBarInput:
    return ResearchBarInput(
        trading_date=trading_date,
        open=close,
        high=close,
        low=close,
        close=close,
        volume=1000,
        data_quality="primary",
        source=_SOURCE,
    )


def test_compute_forward_returns_with_sufficient_bars() -> None:
    # NYSE sessions after 2024-01-02: need bars through ~20 sessions later
    bars = [
        _bar(_AS_OF, Decimal("100")),
        _bar(date(2024, 1, 3), Decimal("101")),
        _bar(date(2024, 1, 4), Decimal("102")),
        _bar(date(2024, 1, 5), Decimal("103")),
        _bar(date(2024, 1, 8), Decimal("104")),
        _bar(date(2024, 1, 9), Decimal("105")),
    ]
    label = compute_forward_total_return_labels(
        _snapshot(),
        bars,
        calendar_name="NYSE",
        horizons=(5,),
    )
    assert label.labels["forward_return_5"] == 0.05
    assert label.label_end_dates["forward_return_5"] == "2024-01-09"


def test_insufficient_forward_bars_fail_closed() -> None:
    bars = [_bar(_AS_OF, Decimal("100"))]
    with pytest.raises(OutcomeLabelUnavailableError) as exc_info:
        compute_forward_total_return_labels(
            _snapshot(),
            bars,
            calendar_name="NYSE",
            horizons=(5,),
        )
    assert exc_info.value.reason == OutcomeLabelReason.INSUFFICIENT_FORWARD_BARS


def test_snapshot_forward_bar_shortfall_full_horizon_from_as_of_only() -> None:
    bars = [_bar(_AS_OF, Decimal("100"))]
    shortfall = snapshot_forward_bar_shortfall(
        _snapshot(),
        bars,
        calendar_name="NYSE",
        horizons=(5,),
    )
    assert shortfall == 5


def test_snapshot_forward_bar_shortfall_partial_progress() -> None:
    bars = [
        _bar(_AS_OF, Decimal("100")),
        _bar(date(2024, 1, 3), Decimal("101")),
        _bar(date(2024, 1, 4), Decimal("102")),
        _bar(date(2024, 1, 5), Decimal("103")),
    ]
    shortfall = snapshot_forward_bar_shortfall(
        _snapshot(),
        bars,
        calendar_name="NYSE",
        horizons=(5,),
    )
    # Have 3 sessions after as_of; need end = 5th session (2024-01-09) → shortfall 2
    assert shortfall == 2
    assert forward_horizon_end_date(_AS_OF, 5, "NYSE") == date(2024, 1, 9)


def test_snapshot_forward_bar_shortfall_ready_is_zero() -> None:
    bars = [
        _bar(_AS_OF, Decimal("100")),
        _bar(date(2024, 1, 3), Decimal("101")),
        _bar(date(2024, 1, 4), Decimal("102")),
        _bar(date(2024, 1, 5), Decimal("103")),
        _bar(date(2024, 1, 8), Decimal("104")),
        _bar(date(2024, 1, 9), Decimal("105")),
    ]
    shortfall = snapshot_forward_bar_shortfall(
        _snapshot(),
        bars,
        calendar_name="NYSE",
        horizons=(5,),
    )
    assert shortfall == 0


def test_snapshot_forward_bar_shortfall_no_as_of_is_null() -> None:
    bars = [_bar(date(2024, 1, 3), Decimal("101"))]
    shortfall = snapshot_forward_bar_shortfall(
        _snapshot(),
        bars,
        calendar_name="NYSE",
        horizons=(5,),
    )
    assert shortfall is None


def test_snapshot_required_label_end_date_from_as_of() -> None:
    bars = [_bar(_AS_OF, Decimal("100"))]
    end = snapshot_required_label_end_date(
        _snapshot(),
        bars,
        calendar_name="NYSE",
        horizons=(5,),
    )
    assert end == date(2024, 1, 9)
    assert end == forward_horizon_end_date(_AS_OF, 5, "NYSE")


def test_snapshot_required_label_end_date_no_as_of_is_null() -> None:
    bars = [_bar(date(2024, 1, 3), Decimal("101"))]
    end = snapshot_required_label_end_date(
        _snapshot(),
        bars,
        calendar_name="NYSE",
        horizons=(5,),
    )
    assert end is None


def test_missing_snapshot_id_fail_closed() -> None:
    with pytest.raises(OutcomeLabelUnavailableError) as exc_info:
        compute_forward_total_return_labels(
            _snapshot(id=None),
            [],
            calendar_name="NYSE",
            horizons=(5,),
        )
    assert exc_info.value.reason == OutcomeLabelReason.ASSESSMENT_NOT_FOUND
