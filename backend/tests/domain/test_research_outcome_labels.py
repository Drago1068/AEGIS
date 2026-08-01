"""Unit tests for forward-return outcome label computation (ADR-0014)."""

from __future__ import annotations

from collections.abc import Sequence
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
    OutcomeLabelData,
    OutcomeLabelReason,
    OutcomeLabelUnavailableError,
    compute_forward_total_return_labels,
    forward_horizon_end_date,
    label_covers_configured_horizons,
    ready_forward_horizons,
    snapshot_forward_bar_shortfall,
    snapshot_label_source_max_bar_date,
    snapshot_last_available_label_bar_date,
    snapshot_required_label_end_date,
    stored_bar_calendar_lag_trading_days,
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


def test_ready_forward_horizons_partial_when_tip_blocked() -> None:
    bars = [
        _bar(_AS_OF, Decimal("100")),
        _bar(date(2024, 1, 3), Decimal("101")),
        _bar(date(2024, 1, 4), Decimal("102")),
        _bar(date(2024, 1, 5), Decimal("103")),
        _bar(date(2024, 1, 8), Decimal("104")),
        _bar(date(2024, 1, 9), Decimal("105")),
    ]
    assert ready_forward_horizons(_snapshot(), bars, calendar_name="NYSE") == (5,)
    label = compute_forward_total_return_labels(
        _snapshot(),
        bars,
        calendar_name="NYSE",
        horizons=(5,),
    )
    assert set(label.labels) == {"forward_return_5"}
    assert "forward_return_20" not in label.labels


def test_ready_forward_horizons_empty_when_none_ready() -> None:
    bars = [_bar(_AS_OF, Decimal("100"))]
    assert ready_forward_horizons(_snapshot(), bars, calendar_name="NYSE") == ()


def test_label_covers_configured_horizons_partial_and_complete() -> None:
    assert not label_covers_configured_horizons({"forward_return_5": 0.05})
    assert label_covers_configured_horizons(
        {"forward_return_5": 0.05, "forward_return_20": 0.1}
    )
    assert not label_covers_configured_horizons({})


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


def test_snapshot_forward_bar_shortfall_min_horizon_differs_from_max() -> None:
    bars = [
        _bar(_AS_OF, Decimal("100")),
        _bar(date(2024, 1, 3), Decimal("101")),
        _bar(date(2024, 1, 4), Decimal("102")),
        _bar(date(2024, 1, 5), Decimal("103")),
        _bar(date(2024, 1, 8), Decimal("104")),
        _bar(date(2024, 1, 9), Decimal("105")),
    ]
    assert (
        snapshot_forward_bar_shortfall(
            _snapshot(),
            bars,
            calendar_name="NYSE",
            horizons=(5,),
        )
        == 0
    )
    assert (
        snapshot_forward_bar_shortfall(
            _snapshot(),
            bars,
            calendar_name="NYSE",
            horizons=(5, 20),
        )
        == 15
    )


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


def test_snapshot_required_label_end_date_min_differs_from_max() -> None:
    bars = [_bar(_AS_OF, Decimal("100"))]
    min_end = snapshot_required_label_end_date(
        _snapshot(),
        bars,
        calendar_name="NYSE",
        horizons=(5,),
    )
    max_end = snapshot_required_label_end_date(
        _snapshot(),
        bars,
        calendar_name="NYSE",
        horizons=(5, 20),
    )
    assert min_end == date(2024, 1, 9)
    assert max_end == forward_horizon_end_date(_AS_OF, 20, "NYSE")
    assert min_end is not None and max_end is not None and min_end < max_end


def test_stored_bar_calendar_lag_current_tip_is_zero() -> None:
    bars = [_bar(_AS_OF, Decimal("100"))]
    lag = stored_bar_calendar_lag_trading_days(
        _snapshot(),
        bars,
        calendar_name="NYSE",
        reference_date=_AS_OF,
    )
    assert lag == 0
    assert snapshot_label_source_max_bar_date(_snapshot(), bars) == _AS_OF


def test_stored_bar_calendar_lag_counts_sessions_behind_reference() -> None:
    bars = [_bar(_AS_OF, Decimal("100"))]
    # 2024-01-02 tip vs reference 2024-01-05 (Thu): sessions 1/3, 1/4, 1/5 => 3
    lag = stored_bar_calendar_lag_trading_days(
        _snapshot(),
        bars,
        calendar_name="NYSE",
        reference_date=date(2024, 1, 5),
    )
    assert lag == 3


def test_stored_bar_calendar_lag_null_when_no_closes() -> None:
    lag = stored_bar_calendar_lag_trading_days(
        _snapshot(),
        [],
        calendar_name="NYSE",
        reference_date=date(2024, 1, 5),
    )
    assert lag is None
    assert snapshot_label_source_max_bar_date(_snapshot(), []) is None


def test_snapshot_required_label_end_date_no_as_of_is_null() -> None:
    bars = [_bar(date(2024, 1, 3), Decimal("101"))]
    end = snapshot_required_label_end_date(
        _snapshot(),
        bars,
        calendar_name="NYSE",
        horizons=(5,),
    )
    assert end is None


def test_snapshot_last_available_label_bar_date_as_of_only() -> None:
    bars = [_bar(_AS_OF, Decimal("100"))]
    last = snapshot_last_available_label_bar_date(
        _snapshot(),
        bars,
        calendar_name="NYSE",
        horizons=(5,),
    )
    assert last == _AS_OF


def test_snapshot_last_available_label_bar_date_partial_forward() -> None:
    bars = [
        _bar(_AS_OF, Decimal("100")),
        _bar(date(2024, 1, 3), Decimal("101")),
        _bar(date(2024, 1, 5), Decimal("103")),
    ]
    last = snapshot_last_available_label_bar_date(
        _snapshot(),
        bars,
        calendar_name="NYSE",
        horizons=(5,),
    )
    assert last == date(2024, 1, 5)


def test_snapshot_last_available_label_bar_date_no_as_of_is_null() -> None:
    bars = [_bar(date(2024, 1, 3), Decimal("101"))]
    last = snapshot_last_available_label_bar_date(
        _snapshot(),
        bars,
        calendar_name="NYSE",
        horizons=(5,),
    )
    assert last is None


def test_missing_snapshot_id_fail_closed() -> None:
    with pytest.raises(OutcomeLabelUnavailableError) as exc_info:
        compute_forward_total_return_labels(
            _snapshot(id=None),
            [],
            calendar_name="NYSE",
            horizons=(5,),
        )
    assert exc_info.value.reason == OutcomeLabelReason.ASSESSMENT_NOT_FOUND


class _MemAssessmentStore:
    def __init__(self, snapshot: ResearchAssessmentSnapshotData | None) -> None:
        self._snapshot = snapshot

    async def get_by_id(self, assessment_id: int) -> ResearchAssessmentSnapshotData | None:
        if self._snapshot is None or self._snapshot.id != assessment_id:
            return None
        return self._snapshot


class _MemBarReader:
    def __init__(self, bars: list[ResearchBarInput]) -> None:
        self._bars = bars

    async def list_recent_bars(self, symbol: str, limit: int) -> list[ResearchBarInput]:
        return list(self._bars)[:limit]


class _MemLabelStore:
    def __init__(self) -> None:
        self.inserted: list[OutcomeLabelData] = []

    async def insert(self, label: OutcomeLabelData) -> OutcomeLabelData:
        stored = OutcomeLabelData(
            id=len(self.inserted) + 1,
            assessment_snapshot_id=label.assessment_snapshot_id,
            symbol=label.symbol,
            label_method_id=label.label_method_id,
            label_method_version=label.label_method_version,
            state=label.state,
            as_of_trading_date=label.as_of_trading_date,
            computed_at=label.computed_at,
            labels=dict(label.labels),
            label_end_dates=dict(label.label_end_dates),
            schema_version=label.schema_version,
            bar_source=label.bar_source,
        )
        self.inserted.append(stored)
        return stored

    async def get_latest_for_assessment(
        self, assessment_snapshot_id: int
    ) -> OutcomeLabelData | None:
        for label in reversed(self.inserted):
            if label.assessment_snapshot_id == assessment_snapshot_id:
                return label
        return None

    async def list_for_assessment(
        self,
        assessment_snapshot_id: int,
        limit: int,
        *,
        symbol: str | None = None,
    ) -> list[OutcomeLabelData]:
        rows = [
            label
            for label in reversed(self.inserted)
            if label.assessment_snapshot_id == assessment_snapshot_id
            and (symbol is None or label.symbol.upper() == symbol.upper())
        ]
        return rows[:limit]

    async def assessment_ids_with_labels(
        self,
        symbol: str,
        assessment_ids: Sequence[int],
        *,
        label_method_id: str,
    ) -> set[int]:
        return {
            label.assessment_snapshot_id
            for label in self.inserted
            if label.symbol.upper() == symbol.upper()
            and label.label_method_id == label_method_id
            and label.assessment_snapshot_id in assessment_ids
        }

    async def latest_labels_for_assessments(
        self,
        symbol: str,
        assessment_ids: Sequence[int],
        *,
        label_method_id: str,
    ) -> dict[int, OutcomeLabelData]:
        latest: dict[int, OutcomeLabelData] = {}
        for label in reversed(self.inserted):
            if label.symbol.upper() != symbol.upper():
                continue
            if label.label_method_id != label_method_id:
                continue
            if label.assessment_snapshot_id not in assessment_ids:
                continue
            if label.assessment_snapshot_id in latest:
                continue
            latest[label.assessment_snapshot_id] = label
        return latest


@pytest.mark.asyncio
async def test_label_assessment_ready_horizons_persists_partial_only() -> None:
    from aegis.domain.research_outcome_labels import OutcomeLabelService

    bars = [
        _bar(_AS_OF, Decimal("100")),
        _bar(date(2024, 1, 3), Decimal("101")),
        _bar(date(2024, 1, 4), Decimal("102")),
        _bar(date(2024, 1, 5), Decimal("103")),
        _bar(date(2024, 1, 8), Decimal("104")),
        _bar(date(2024, 1, 9), Decimal("105")),
    ]
    store = _MemLabelStore()
    service = OutcomeLabelService(
        _MemAssessmentStore(_snapshot()),
        _MemBarReader(bars),
        store,
        calendar_name="NYSE",
    )
    label = await service.label_assessment_ready_horizons("AAPL", 1)
    assert set(label.labels) == {"forward_return_5"}
    assert len(store.inserted) == 1


@pytest.mark.asyncio
async def test_label_assessment_ready_horizons_fail_closed_when_none_ready() -> None:
    from aegis.domain.research_outcome_labels import OutcomeLabelService

    store = _MemLabelStore()
    service = OutcomeLabelService(
        _MemAssessmentStore(_snapshot()),
        _MemBarReader([_bar(_AS_OF, Decimal("100"))]),
        store,
        calendar_name="NYSE",
    )
    with pytest.raises(OutcomeLabelUnavailableError) as exc_info:
        await service.label_assessment_ready_horizons("AAPL", 1)
    assert exc_info.value.reason == OutcomeLabelReason.INSUFFICIENT_FORWARD_BARS
    assert store.inserted == []


@pytest.mark.asyncio
async def test_assessment_ids_with_complete_labels_skips_partial() -> None:
    from aegis.domain.research_outcome_labels import LABEL_METHOD_ID, OutcomeLabelService

    store = _MemLabelStore()
    await store.insert(
        OutcomeLabelData(
            assessment_snapshot_id=1,
            symbol="AAPL",
            label_method_id=LABEL_METHOD_ID,
            label_method_version=1,
            state="research_only",
            as_of_trading_date=_AS_OF,
            computed_at=datetime(2024, 1, 10, 12, tzinfo=UTC),
            labels={"forward_return_5": 0.05},
            label_end_dates={"forward_return_5": "2024-01-09"},
            schema_version=1,
            bar_source=_SOURCE,
        )
    )
    await store.insert(
        OutcomeLabelData(
            assessment_snapshot_id=2,
            symbol="AAPL",
            label_method_id=LABEL_METHOD_ID,
            label_method_version=1,
            state="research_only",
            as_of_trading_date=_AS_OF,
            computed_at=datetime(2024, 1, 10, 12, tzinfo=UTC),
            labels={"forward_return_5": 0.05, "forward_return_20": 0.1},
            label_end_dates={
                "forward_return_5": "2024-01-09",
                "forward_return_20": "2024-02-01",
            },
            schema_version=1,
            bar_source=_SOURCE,
        )
    )
    service = OutcomeLabelService(
        _MemAssessmentStore(_snapshot()),
        _MemBarReader([]),
        store,
        calendar_name="NYSE",
    )
    complete = await service.assessment_ids_with_complete_labels("AAPL", [1, 2, 3])
    assert complete == {2}
    any_labeled = await service.assessment_ids_with_labels("AAPL", [1, 2, 3])
    assert any_labeled == {1, 2}
