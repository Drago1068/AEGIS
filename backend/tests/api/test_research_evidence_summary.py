"""API tests for research evidence summary (Phase 22, ADR-0023)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from httpx import ASGITransport, AsyncClient

from aegis.api.dependencies import (
    get_outcome_label_service,
    get_research_assessment_service,
    get_research_calibration_repository,
    get_research_calibration_service,
    require_operator,
)
from aegis.api.main import create_app
from aegis.config.settings import Settings
from aegis.domain.research_assessment import ResearchAssessmentSnapshotData, ResearchBarInput
from aegis.domain.research_outcome_labels import (
    LABEL_METHOD_ID,
    OutcomeLabelData,
    OutcomeLabelReason,
    resolve_label_bar_source,
)
from aegis.domain.research_probability_calibration import (
    CALIBRATION_METHOD_ID,
    CalibrationReadinessData,
    CalibrationReadinessStatus,
    ProbabilityCalibrationData,
)
from aegis.persistence.models import Operator


def _operator() -> Operator:
    return Operator(
        id=1,
        username="operator",
        password_hash="unused",
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
        updated_at=datetime(2024, 1, 1, tzinfo=UTC),
    )


def _snapshot(
    *,
    snapshot_id: int = 1,
    input_source: str = "alpha_vantage",
    component_source: str | None = None,
    coverage_sources: list[str] | None = None,
    as_of: date = date(2024, 1, 26),
) -> ResearchAssessmentSnapshotData:
    components: dict[str, float | str | list[str]] = {"research_index": 0.46}
    if component_source is not None:
        components["component_source"] = component_source
    if coverage_sources is not None:
        components["coverage_sources"] = coverage_sources
    return ResearchAssessmentSnapshotData(
        id=snapshot_id,
        symbol="AAPL",
        method_id="daily_bar_research_v1",
        method_version=1,
        state="research_only",
        as_of_trading_date=as_of,
        event_time=datetime(as_of.year, as_of.month, as_of.day, 23, 59, 59, tzinfo=UTC),
        computed_at=datetime(as_of.year, as_of.month, as_of.day, 18, 0, tzinfo=UTC),
        coverage_confidence=0.95,
        probability_confidence=None,
        components=components,
        schema_version=1,
        input_source=input_source,
        lookback_start_date=date(2023, 12, 27),
        lookback_end_date=as_of,
        bar_count=20,
    )


def _readiness() -> CalibrationReadinessData:
    return CalibrationReadinessData(
        symbol="AAPL",
        status=CalibrationReadinessStatus.INSUFFICIENT_LABELED_CORPUS,
        assessment_snapshot_id=1,
        research_index=0.46,
        corpus_count=3,
        bucket_count=2,
        min_corpus=10,
        min_bucket=5,
        index_bucket_width=0.15,
        calibration_method_id=CALIBRATION_METHOD_ID,
        detail="need at least 10 labeled historical examples, found 3",
    )


def _label(*, assessment_snapshot_id: int = 1) -> OutcomeLabelData:
    return OutcomeLabelData(
        id=10,
        assessment_snapshot_id=assessment_snapshot_id,
        symbol="AAPL",
        label_method_id=LABEL_METHOD_ID,
        label_method_version=1,
        state="research_only",
        as_of_trading_date=date(2024, 1, 26),
        computed_at=datetime(2024, 1, 26, 19, 0, tzinfo=UTC),
        labels={"forward_return_5": 0.05},
        label_end_dates={"forward_return_5": "2024-02-02"},
        schema_version=1,
        bar_source="alpha_vantage",
    )


def _calibration() -> ProbabilityCalibrationData:
    return ProbabilityCalibrationData(
        id=7,
        assessment_snapshot_id=1,
        symbol="AAPL",
        calibration_method_id=CALIBRATION_METHOD_ID,
        calibration_method_version=1,
        state="research_only",
        computed_at=datetime(2024, 1, 26, 20, 0, tzinfo=UTC),
        probability_confidence=0.62,
        corpus_count=12,
        bucket_count=6,
        schema_version=1,
    )


class _FakeAssessmentService:
    def __init__(self, listed: list[ResearchAssessmentSnapshotData] | None = None) -> None:
        self._listed = listed or []

    async def list_assessments(
        self, symbol: str, limit: int
    ) -> list[ResearchAssessmentSnapshotData]:
        return self._listed[:limit]

    async def latest_assessment(self, symbol: str) -> ResearchAssessmentSnapshotData | None:
        return self._listed[0] if self._listed else None


class _FakeOutcomeLabelService:
    def __init__(
        self,
        listed: list[OutcomeLabelData] | None = None,
        *,
        label_ready: bool = False,
        label_block_reason: str | None = "insufficient_forward_bars",
        labelable_as_of: date | None = None,
        unlabeled_labelable_as_of: date | None = None,
        forward_bar_shortfall: int | None = 20,
        required_label_end_date: date | None = date(2024, 2, 26),
        last_available_label_bar_date: date | None = date(2024, 1, 26),
        min_horizon_forward_bar_shortfall: int | None = 5,
        min_horizon_required_label_end_date: date | None = date(2024, 2, 2),
        stored_bar_calendar_lag_trading_days: int | None = 2,
        resolve_bars: list[ResearchBarInput] | None = None,
    ) -> None:
        self._listed = listed or []
        self._resolve_bars = resolve_bars
        self._label_ready = label_ready
        self._label_block_reason = None if label_ready else label_block_reason
        self._labelable_as_of = labelable_as_of
        self._unlabeled_labelable_as_of = unlabeled_labelable_as_of
        self._forward_bar_shortfall = 0 if label_ready else forward_bar_shortfall
        self._min_horizon_forward_bar_shortfall = (
            0 if label_ready else min_horizon_forward_bar_shortfall
        )
        self._stored_bar_calendar_lag_trading_days = (
            0 if label_ready else stored_bar_calendar_lag_trading_days
        )
        if not label_ready and label_block_reason == "no_as_of_bar":
            self._required_label_end_date = None
            self._last_available_label_bar_date = None
            self._min_horizon_forward_bar_shortfall = None
            self._min_horizon_required_label_end_date = None
        else:
            self._required_label_end_date = required_label_end_date
            self._last_available_label_bar_date = last_available_label_bar_date
            self._min_horizon_required_label_end_date = min_horizon_required_label_end_date

    async def list_labels_for_assessment(
        self, symbol: str, assessment_snapshot_id: int, limit: int
    ) -> list[OutcomeLabelData]:
        matched = [
            row
            for row in self._listed
            if row.assessment_snapshot_id == assessment_snapshot_id
        ]
        return matched[:limit]

    async def resolve_label_bar_source_for_assessment(
        self,
        symbol: str,
        snapshot: ResearchAssessmentSnapshotData,
    ) -> str:
        _ = symbol
        return resolve_label_bar_source(snapshot, self._resolve_bars)

    async def assessment_ids_with_labels(
        self,
        symbol: str,
        assessment_ids: list[int],
        *,
        label_method_id: str = LABEL_METHOD_ID,
    ) -> set[int]:
        _ = label_method_id
        labeled = {row.assessment_snapshot_id for row in self._listed}
        return {item for item in assessment_ids if item in labeled}

    async def is_assessment_label_ready(
        self, symbol: str, snapshot: ResearchAssessmentSnapshotData
    ) -> bool:
        ready, _reason = await self.label_readiness_for_assessment(symbol, snapshot)
        return ready

    async def label_readiness_for_assessment(
        self, symbol: str, snapshot: ResearchAssessmentSnapshotData
    ) -> tuple[bool, OutcomeLabelReason | None]:
        _ = symbol, snapshot
        if self._label_ready:
            return True, None
        reason = (
            OutcomeLabelReason(self._label_block_reason)
            if self._label_block_reason is not None
            else OutcomeLabelReason.INSUFFICIENT_FORWARD_BARS
        )
        return False, reason

    async def scan_label_diagnostics(
        self,
        symbol: str,
        snapshots_newest_first: list[ResearchAssessmentSnapshotData],
        *,
        labeled_assessment_ids: set[int] | None = None,
        reference_date: date | None = None,
    ) -> tuple[
        bool | None,
        OutcomeLabelReason | None,
        date | None,
        date | None,
        int,
        int | None,
        date | None,
        date | None,
        int | None,
        date | None,
        int | None,
    ]:
        _ = reference_date
        if not snapshots_newest_first:
            return None, None, None, None, 0, None, None, None, None, None, None
        labeled = labeled_assessment_ids
        if labeled is None:
            labeled = {row.assessment_snapshot_id for row in self._listed}
        ready, reason = await self.label_readiness_for_assessment(
            symbol, snapshots_newest_first[0]
        )
        labelable = (
            snapshots_newest_first[0].as_of_trading_date
            if ready
            else self._labelable_as_of
        )
        unlabeled_labelable: date | None = None
        unlabeled_ready_count = 0
        if ready:
            latest_id = snapshots_newest_first[0].id
            if latest_id is not None and latest_id not in labeled:
                unlabeled_labelable = snapshots_newest_first[0].as_of_trading_date
                unlabeled_ready_count = 1
        elif self._unlabeled_labelable_as_of is not None:
            unlabeled_labelable = self._unlabeled_labelable_as_of
            unlabeled_ready_count = 1
        shortfall: int | None
        min_shortfall: int | None
        if ready:
            shortfall = 0
            min_shortfall = 0
        elif reason == OutcomeLabelReason.NO_AS_OF_BAR:
            shortfall = None
            min_shortfall = None
        else:
            shortfall = self._forward_bar_shortfall
            min_shortfall = self._min_horizon_forward_bar_shortfall
        end_date: date | None
        last_bar: date | None
        min_end: date | None
        if reason == OutcomeLabelReason.NO_AS_OF_BAR and not ready:
            end_date = None
            last_bar = None
            min_end = None
        else:
            end_date = self._required_label_end_date
            last_bar = self._last_available_label_bar_date
            min_end = self._min_horizon_required_label_end_date
        return (
            ready,
            reason,
            labelable,
            unlabeled_labelable,
            unlabeled_ready_count,
            shortfall,
            end_date,
            last_bar,
            min_shortfall,
            min_end,
            self._stored_bar_calendar_lag_trading_days,
        )


class _FakeCalibrationService:
    def __init__(
        self,
        *,
        readiness: CalibrationReadinessData,
        listed: list[ProbabilityCalibrationData] | None = None,
    ) -> None:
        self._readiness = readiness
        self._listed = listed or []

    async def evaluate_readiness(
        self, symbol: str, snapshot: ResearchAssessmentSnapshotData | None
    ) -> CalibrationReadinessData:
        return self._readiness

    async def list_calibrations_for_assessment(
        self, symbol: str, assessment_snapshot_id: int, limit: int
    ) -> list[ProbabilityCalibrationData]:
        return self._listed[:limit]


class _FakeCalibrationRepository:
    async def get_latest_for_assessment(
        self, assessment_snapshot_id: int
    ) -> ProbabilityCalibrationData | None:
        return None


def _client(
    *,
    assessments: list[ResearchAssessmentSnapshotData] | None = None,
    labels: list[OutcomeLabelData] | None = None,
    calibrations: list[ProbabilityCalibrationData] | None = None,
    readiness: CalibrationReadinessData | None = None,
    label_ready: bool = False,
    label_block_reason: str | None = "insufficient_forward_bars",
    labelable_as_of: date | None = None,
    unlabeled_labelable_as_of: date | None = None,
    forward_bar_shortfall: int | None = 20,
    required_label_end_date: date | None = date(2024, 2, 26),
    last_available_label_bar_date: date | None = date(2024, 1, 26),
    min_horizon_forward_bar_shortfall: int | None = 5,
    min_horizon_required_label_end_date: date | None = date(2024, 2, 2),
    stored_bar_calendar_lag_trading_days: int | None = 2,
    resolve_bars: list[ResearchBarInput] | None = None,
) -> AsyncClient:
    app = create_app(settings=Settings(environment="test", ingestion_schedule_enabled=False))
    app.dependency_overrides[require_operator] = _operator
    app.dependency_overrides[get_research_assessment_service] = lambda: _FakeAssessmentService(
        assessments
    )
    app.dependency_overrides[get_outcome_label_service] = lambda: _FakeOutcomeLabelService(
        labels,
        label_ready=label_ready,
        label_block_reason=label_block_reason,
        labelable_as_of=labelable_as_of,
        unlabeled_labelable_as_of=unlabeled_labelable_as_of,
        forward_bar_shortfall=forward_bar_shortfall,
        required_label_end_date=required_label_end_date,
        last_available_label_bar_date=last_available_label_bar_date,
        min_horizon_forward_bar_shortfall=min_horizon_forward_bar_shortfall,
        min_horizon_required_label_end_date=min_horizon_required_label_end_date,
        stored_bar_calendar_lag_trading_days=stored_bar_calendar_lag_trading_days,
        resolve_bars=resolve_bars,
    )
    app.dependency_overrides[get_research_calibration_service] = lambda: _FakeCalibrationService(
        readiness=readiness or _readiness(),
        listed=calibrations,
    )
    app.dependency_overrides[get_research_calibration_repository] = lambda: (
        _FakeCalibrationRepository()
    )
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


async def test_evidence_summary_empty_symbol() -> None:
    readiness = CalibrationReadinessData(
        symbol="AAPL",
        status=CalibrationReadinessStatus.NO_ASSESSMENT,
        assessment_snapshot_id=None,
        research_index=None,
        corpus_count=0,
        bucket_count=0,
        min_corpus=10,
        min_bucket=5,
        index_bucket_width=0.15,
        calibration_method_id=CALIBRATION_METHOD_ID,
        detail="no assessment",
    )
    async with _client(readiness=readiness) as client:
        response = await client.get("/research/AAPL/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "AAPL"
    assert body["state"] == "research_only"
    assert body["latest_assessment"] is None
    assert body["latest_outcome_label"] is None
    assert body["latest_calibration"] is None
    assert body["assessment_count"] == 0
    assert body["labeled_assessment_count"] == 0
    assert body["unlabeled_assessment_count"] == 0
    assert body["outcome_label_count"] == 0
    assert body["calibration_count"] == 0
    assert body["latest_component_source"] is None
    assert body["latest_resolved_label_bar_source"] is None
    assert body["mixed_component_source_assessment_count"] == 0
    assert body["mixed_unlabeled_assessment_count"] == 0
    assert body["mixed_labeled_assessment_count"] == 0
    assert body["latest_mixed_label_bar_source"] is None
    assert body["most_recent_labeled_assessment_id"] is None
    assert body["most_recent_labeled_outcome_label"] is None
    assert body["most_recent_labeled_outcome_label_id"] is None
    assert body["most_recent_labeled_outcome_label_method_id"] is None
    assert body["most_recent_labeled_outcome_label_method_version"] is None
    assert body["most_recent_labeled_outcome_label_schema_version"] is None
    assert body["most_recent_labeled_outcome_label_state"] is None
    assert body["most_recent_labeled_outcome_label_bar_source"] is None
    assert body["most_recent_labeled_outcome_label_computed_at"] is None
    assert body["most_recent_labeled_outcome_label_as_of_trading_date"] is None
    assert body["scan_labeled_freshness_lag_trading_days"] is None
    assert body["latest_assessment_is_label_ready"] is None
    assert body["latest_assessment_label_block_reason"] is None
    assert body["most_recent_labelable_as_of_trading_date"] is None
    assert body["most_recent_unlabeled_labelable_as_of_trading_date"] is None
    assert body["scan_unlabeled_label_ready_count"] == 0
    assert body["most_recent_unlabeled_assessment_id"] is None
    assert body["most_recent_unlabeled_as_of_trading_date"] is None
    assert body["latest_assessment_forward_bar_shortfall"] is None
    assert body["latest_assessment_required_label_end_date"] is None
    assert body["latest_assessment_last_available_label_bar_date"] is None
    assert body["latest_assessment_min_horizon_forward_bar_shortfall"] is None
    assert body["latest_assessment_min_horizon_required_label_end_date"] is None
    assert body["stored_bar_calendar_lag_trading_days"] is None
    assert body["latest_coverage_confidence"] is None
    assert body["latest_research_index"] is None
    assert body["latest_as_of_trading_date"] is None
    assert body["latest_bar_count"] is None
    assert body["latest_input_source"] is None
    assert body["latest_method_id"] is None
    assert body["latest_method_version"] is None
    assert body["latest_lookback_end_date"] is None
    assert body["latest_lookback_start_date"] is None
    assert body["latest_schema_version"] is None
    assert body["latest_computed_at"] is None
    assert body["latest_event_time"] is None
    assert body["latest_probability_confidence"] is None
    assert body["latest_assessment_id"] is None
    assert body["latest_outcome_label_id"] is None
    assert body["latest_outcome_label_computed_at"] is None
    assert body["latest_outcome_label_method_id"] is None
    assert body["latest_outcome_label_method_version"] is None
    assert body["latest_outcome_label_schema_version"] is None
    assert body["latest_outcome_label_state"] is None
    assert body["latest_outcome_label_bar_source"] is None
    assert body["latest_outcome_label_as_of_trading_date"] is None
    assert body["latest_calibration_id"] is None
    assert body["latest_calibration_horizon_key"] is None
    assert body["latest_calibration_computed_at"] is None
    assert body["latest_calibration_corpus_count"] is None
    assert body["latest_calibration_bucket_count"] is None
    assert body["latest_calibration_method_id"] is None
    assert body["latest_calibration_method_version"] is None
    assert body["latest_calibration_schema_version"] is None
    assert body["latest_calibration_state"] is None
    assert body["latest_calibration_probability_confidence"] is None
    assert body["latest_calibration_assessment_snapshot_id"] is None
    assert body["calibration_readiness"]["status"] == "no_assessment"
    assert "never invented" in body["detail"].lower() or "not invented" in body["detail"].lower()


async def test_evidence_summary_with_assessment_and_histories() -> None:
    async with _client(
        assessments=[_snapshot()],
        labels=[_label()],
        calibrations=[_calibration()],
        label_ready=True,
    ) as client:
        response = await client.get("/research/aapl/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "AAPL"
    assert body["latest_assessment"]["id"] == 1
    assert body["latest_assessment"]["probability_confidence"] is None
    assert body["latest_assessment_is_label_ready"] is True
    assert body["latest_assessment_label_block_reason"] is None
    assert body["most_recent_labelable_as_of_trading_date"] == "2024-01-26"
    assert body["most_recent_unlabeled_labelable_as_of_trading_date"] is None
    assert body["scan_unlabeled_label_ready_count"] == 0
    assert body["most_recent_unlabeled_assessment_id"] is None
    assert body["most_recent_unlabeled_as_of_trading_date"] is None
    assert body["latest_assessment_forward_bar_shortfall"] == 0
    assert body["latest_assessment_required_label_end_date"] == "2024-02-26"
    assert body["latest_assessment_last_available_label_bar_date"] == "2024-01-26"
    assert body["latest_assessment_min_horizon_forward_bar_shortfall"] == 0
    assert body["latest_assessment_min_horizon_required_label_end_date"] == "2024-02-02"
    assert body["stored_bar_calendar_lag_trading_days"] == 0
    assert body["latest_coverage_confidence"] == 0.95
    assert body["latest_research_index"] == 0.46
    assert body["latest_as_of_trading_date"] == "2024-01-26"
    assert body["latest_bar_count"] == 20
    assert body["latest_input_source"] == "alpha_vantage"
    assert body["latest_method_id"] == "daily_bar_research_v1"
    assert body["latest_method_version"] == 1
    assert body["latest_lookback_end_date"] == "2024-01-26"
    assert body["latest_lookback_start_date"] == "2023-12-27"
    assert body["latest_schema_version"] == 1
    assert body["latest_computed_at"] == "2024-01-26T18:00:00Z"
    assert body["latest_event_time"] == "2024-01-26T23:59:59Z"
    assert body["latest_probability_confidence"] is None
    assert body["latest_assessment_id"] == 1
    assert body["latest_outcome_label_id"] == 10
    assert body["latest_outcome_label_computed_at"] == "2024-01-26T19:00:00Z"
    assert body["latest_outcome_label_method_id"] == "forward_total_return_v1"
    assert body["latest_outcome_label_method_version"] == 1
    assert body["latest_outcome_label_schema_version"] == 1
    assert body["latest_outcome_label_state"] == "research_only"
    assert body["latest_outcome_label_bar_source"] == "alpha_vantage"
    assert body["latest_outcome_label_as_of_trading_date"] == "2024-01-26"
    assert body["latest_calibration_id"] == 7
    assert body["latest_calibration_horizon_key"] == "forward_return_5"
    assert body["latest_calibration_computed_at"] == "2024-01-26T20:00:00Z"
    assert body["latest_calibration_corpus_count"] == 12
    assert body["latest_calibration_bucket_count"] == 6
    assert body["latest_calibration_method_id"] == "research_calibration_v1"
    assert body["latest_calibration_method_version"] == 1
    assert body["latest_calibration_schema_version"] == 1
    assert body["latest_calibration_state"] == "research_only"
    assert body["latest_calibration_probability_confidence"] == 0.62
    assert body["latest_calibration_assessment_snapshot_id"] == 1
    assert body["latest_outcome_label"]["labels"]["forward_return_5"] == 0.05
    assert body["latest_calibration"]["probability_confidence"] == 0.62
    assert body["assessment_count"] == 1
    assert body["labeled_assessment_count"] == 1
    assert body["unlabeled_assessment_count"] == 0
    assert body["outcome_label_count"] == 1
    assert body["calibration_count"] == 1
    assert body["state"] == "research_only"
    assert body["latest_component_source"] == "alpha_vantage"
    assert body["latest_resolved_label_bar_source"] == "alpha_vantage"
    assert body["mixed_component_source_assessment_count"] == 0
    assert body["mixed_unlabeled_assessment_count"] == 0
    assert body["mixed_labeled_assessment_count"] == 0
    assert body["latest_mixed_label_bar_source"] is None
    assert body["most_recent_labeled_assessment_id"] == 1
    assert body["most_recent_labeled_outcome_label"]["labels"]["forward_return_5"] == 0.05
    assert body["most_recent_labeled_outcome_label_id"] == 10
    assert body["most_recent_labeled_outcome_label_method_id"] == "forward_total_return_v1"
    assert body["most_recent_labeled_outcome_label_method_version"] == 1
    assert body["most_recent_labeled_outcome_label_schema_version"] == 1
    assert body["most_recent_labeled_outcome_label_state"] == "research_only"
    assert body["most_recent_labeled_outcome_label_bar_source"] == "alpha_vantage"
    assert body["most_recent_labeled_outcome_label_computed_at"] == "2024-01-26T19:00:00Z"
    assert body["most_recent_labeled_outcome_label_as_of_trading_date"] == "2024-01-26"
    assert body["scan_labeled_freshness_lag_trading_days"] == 0
    assert body["latest_outcome_label_id"] == 10


async def test_evidence_summary_scan_labeled_freshness_lag_trading_days() -> None:
    """Phase 229: lag uses NYSE trading days between labeled as_of and latest as_of."""

    unlabeled_latest = ResearchAssessmentSnapshotData(
        id=2,
        symbol="AAPL",
        method_id="daily_bar_research_v1",
        method_version=1,
        state="research_only",
        as_of_trading_date=date(2024, 2, 9),
        event_time=datetime(2024, 2, 9, 23, 59, 59, tzinfo=UTC),
        computed_at=datetime(2024, 2, 9, 18, 0, tzinfo=UTC),
        coverage_confidence=0.95,
        probability_confidence=None,
        components={"research_index": 0.5},
        schema_version=1,
        input_source="alpha_vantage",
        lookback_start_date=date(2024, 1, 12),
        lookback_end_date=date(2024, 2, 9),
        bar_count=20,
    )
    labeled_older = _snapshot(snapshot_id=1)
    async with _client(
        assessments=[unlabeled_latest, labeled_older],
        labels=[_label()],
    ) as client:
        response = await client.get("/research/AAPL/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["latest_as_of_trading_date"] == "2024-02-09"
    assert body["most_recent_labeled_outcome_label_as_of_trading_date"] == "2024-01-26"
    assert body["latest_outcome_label_id"] is None
    assert body["scan_labeled_freshness_lag_trading_days"] == 10


async def test_evidence_summary_latest_assessment_is_label_ready_false() -> None:
    async with _client(
        assessments=[_snapshot()],
        labels=[],
        label_ready=False,
    ) as client:
        response = await client.get("/research/AAPL/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["latest_assessment_id"] == 1
    assert body["latest_outcome_label_id"] is None
    assert body["latest_assessment_is_label_ready"] is False
    assert body["latest_assessment_label_block_reason"] == "insufficient_forward_bars"
    assert body["latest_assessment_forward_bar_shortfall"] == 20
    assert body["latest_assessment_required_label_end_date"] == "2024-02-26"
    assert body["latest_assessment_last_available_label_bar_date"] == "2024-01-26"
    assert body["latest_assessment_min_horizon_forward_bar_shortfall"] == 5
    assert body["latest_assessment_min_horizon_required_label_end_date"] == "2024-02-02"
    assert body["stored_bar_calendar_lag_trading_days"] == 2


async def test_evidence_summary_latest_assessment_label_block_reason_no_as_of() -> None:
    async with _client(
        assessments=[_snapshot()],
        labels=[],
        label_ready=False,
        label_block_reason="no_as_of_bar",
        forward_bar_shortfall=None,
    ) as client:
        response = await client.get("/research/AAPL/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["latest_assessment_is_label_ready"] is False
    assert body["latest_assessment_label_block_reason"] == "no_as_of_bar"
    assert body["latest_assessment_forward_bar_shortfall"] is None
    assert body["latest_assessment_required_label_end_date"] is None
    assert body["latest_assessment_last_available_label_bar_date"] is None
    assert body["latest_assessment_min_horizon_forward_bar_shortfall"] is None
    assert body["latest_assessment_min_horizon_required_label_end_date"] is None


async def test_evidence_summary_latest_assessment_forward_bar_shortfall() -> None:
    async with _client(
        assessments=[_snapshot()],
        labels=[],
        label_ready=False,
        forward_bar_shortfall=7,
    ) as client:
        response = await client.get("/research/AAPL/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["latest_assessment_is_label_ready"] is False
    assert body["latest_assessment_forward_bar_shortfall"] == 7


async def test_evidence_summary_latest_assessment_required_label_end_date() -> None:
    async with _client(
        assessments=[_snapshot()],
        labels=[],
        label_ready=False,
        required_label_end_date=date(2024, 3, 15),
    ) as client:
        response = await client.get("/research/AAPL/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["latest_assessment_required_label_end_date"] == "2024-03-15"


async def test_evidence_summary_latest_assessment_last_available_label_bar_date() -> None:
    async with _client(
        assessments=[_snapshot()],
        labels=[],
        label_ready=False,
        last_available_label_bar_date=date(2024, 2, 1),
    ) as client:
        response = await client.get("/research/AAPL/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["latest_assessment_last_available_label_bar_date"] == "2024-02-01"


async def test_evidence_summary_latest_assessment_min_horizon_forward_bar_shortfall() -> None:
    async with _client(
        assessments=[_snapshot()],
        labels=[],
        label_ready=False,
        min_horizon_forward_bar_shortfall=3,
    ) as client:
        response = await client.get("/research/AAPL/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["latest_assessment_min_horizon_forward_bar_shortfall"] == 3


async def test_evidence_summary_latest_assessment_min_horizon_required_label_end_date() -> None:
    async with _client(
        assessments=[_snapshot()],
        labels=[],
        label_ready=False,
        min_horizon_required_label_end_date=date(2024, 2, 9),
    ) as client:
        response = await client.get("/research/AAPL/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["latest_assessment_min_horizon_required_label_end_date"] == "2024-02-09"


async def test_evidence_summary_stored_bar_calendar_lag_trading_days() -> None:
    async with _client(
        assessments=[_snapshot()],
        labels=[],
        label_ready=False,
        stored_bar_calendar_lag_trading_days=4,
    ) as client:
        response = await client.get("/research/AAPL/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["stored_bar_calendar_lag_trading_days"] == 4


async def test_evidence_summary_most_recent_labelable_as_of_trading_date() -> None:
    unlabeled_latest = ResearchAssessmentSnapshotData(
        id=2,
        symbol="AAPL",
        method_id="daily_bar_research_v1",
        method_version=1,
        state="research_only",
        as_of_trading_date=date(2024, 2, 9),
        event_time=datetime(2024, 2, 9, 23, 59, 59, tzinfo=UTC),
        computed_at=datetime(2024, 2, 9, 18, 0, tzinfo=UTC),
        coverage_confidence=0.95,
        probability_confidence=None,
        components={"research_index": 0.5},
        schema_version=1,
        input_source="alpha_vantage",
        lookback_start_date=date(2024, 1, 12),
        lookback_end_date=date(2024, 2, 9),
        bar_count=20,
    )
    async with _client(
        assessments=[unlabeled_latest, _snapshot(snapshot_id=1)],
        labels=[],
        label_ready=False,
        labelable_as_of=date(2024, 1, 26),
    ) as client:
        response = await client.get("/research/AAPL/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["latest_as_of_trading_date"] == "2024-02-09"
    assert body["latest_assessment_is_label_ready"] is False
    assert body["most_recent_labelable_as_of_trading_date"] == "2024-01-26"


async def test_evidence_summary_most_recent_unlabeled_labelable_as_of_trading_date() -> None:
    """Labelable may already be labeled; unlabeled+labelable is the backfill next-target."""

    unlabeled_latest = ResearchAssessmentSnapshotData(
        id=2,
        symbol="AAPL",
        method_id="daily_bar_research_v1",
        method_version=1,
        state="research_only",
        as_of_trading_date=date(2024, 2, 9),
        event_time=datetime(2024, 2, 9, 23, 59, 59, tzinfo=UTC),
        computed_at=datetime(2024, 2, 9, 18, 0, tzinfo=UTC),
        coverage_confidence=0.95,
        probability_confidence=None,
        components={"research_index": 0.5},
        schema_version=1,
        input_source="alpha_vantage",
        lookback_start_date=date(2024, 1, 12),
        lookback_end_date=date(2024, 2, 9),
        bar_count=20,
    )
    async with _client(
        assessments=[unlabeled_latest, _snapshot(snapshot_id=1)],
        labels=[],
        label_ready=False,
        labelable_as_of=date(2024, 1, 26),
        unlabeled_labelable_as_of=date(2024, 1, 20),
    ) as client:
        response = await client.get("/research/AAPL/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["most_recent_labelable_as_of_trading_date"] == "2024-01-26"
    assert body["most_recent_unlabeled_labelable_as_of_trading_date"] == "2024-01-20"
    assert body["scan_unlabeled_label_ready_count"] == 1
    assert body["most_recent_unlabeled_assessment_id"] == 2
    assert body["most_recent_unlabeled_as_of_trading_date"] == "2024-02-09"


async def test_evidence_summary_most_recent_unlabeled_assessment_id() -> None:
    """Newest unlabeled tip id even when that row is not label-ready."""

    unlabeled_latest = ResearchAssessmentSnapshotData(
        id=2,
        symbol="AAPL",
        method_id="daily_bar_research_v1",
        method_version=1,
        state="research_only",
        as_of_trading_date=date(2024, 2, 9),
        event_time=datetime(2024, 2, 9, 23, 59, 59, tzinfo=UTC),
        computed_at=datetime(2024, 2, 9, 18, 0, tzinfo=UTC),
        coverage_confidence=0.95,
        probability_confidence=None,
        components={"research_index": 0.5},
        schema_version=1,
        input_source="alpha_vantage",
        lookback_start_date=date(2024, 1, 12),
        lookback_end_date=date(2024, 2, 9),
        bar_count=20,
    )
    async with _client(
        assessments=[unlabeled_latest, _snapshot(snapshot_id=1)],
        labels=[_label(assessment_snapshot_id=1)],
        label_ready=False,
        labelable_as_of=date(2024, 1, 26),
    ) as client:
        response = await client.get("/research/AAPL/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["latest_assessment_id"] == 2
    assert body["most_recent_labeled_assessment_id"] == 1
    assert body["most_recent_unlabeled_assessment_id"] == 2
    assert body["most_recent_unlabeled_as_of_trading_date"] == "2024-02-09"
    assert body["unlabeled_assessment_count"] == 1
    assert body["scan_unlabeled_label_ready_count"] == 0


async def test_evidence_summary_surfaces_mixed_component_provenance() -> None:
    mixed = _snapshot(
        snapshot_id=2,
        input_source="mixed",
        component_source="mixed",
    )
    primary = _snapshot(snapshot_id=1, component_source="alpha_vantage")
    mixed_label = OutcomeLabelData(
        id=11,
        assessment_snapshot_id=2,
        symbol="AAPL",
        label_method_id=LABEL_METHOD_ID,
        label_method_version=1,
        state="research_only",
        as_of_trading_date=date(2024, 1, 26),
        computed_at=datetime(2024, 1, 26, 19, 0, tzinfo=UTC),
        labels={"forward_return_5": 0.05},
        label_end_dates={"forward_return_5": "2024-02-02"},
        schema_version=1,
        bar_source="polygon",
    )
    async with _client(
        assessments=[mixed, primary],
        labels=[mixed_label],
    ) as client:
        response = await client.get("/research/AAPL/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["latest_component_source"] == "mixed"
    assert body["latest_input_source"] == "mixed"
    assert body["latest_resolved_label_bar_source"] == "polygon"
    assert body["mixed_component_source_assessment_count"] == 1
    assert body["mixed_unlabeled_assessment_count"] == 0
    assert body["mixed_labeled_assessment_count"] == 1
    assert body["labeled_assessment_count"] == 1
    assert body["unlabeled_assessment_count"] == 1
    assert body["latest_mixed_label_bar_source"] == "polygon"


def _as_of_bar(*, trading_date: date, source: str, close: str = "100") -> ResearchBarInput:
    value = Decimal(close)
    return ResearchBarInput(
        trading_date=trading_date,
        open=value,
        high=value,
        low=value,
        close=value,
        volume=1000,
        data_quality="primary",
        source=source,
    )


async def test_evidence_summary_resolves_mixed_label_bar_source_with_bars() -> None:
    """Unlabeled mixed latest assessment resolves concrete source via bars (ADR-0268)."""

    as_of = date(2024, 1, 26)
    mixed = _snapshot(
        snapshot_id=3,
        input_source="mixed",
        component_source="mixed",
        coverage_sources=["polygon", "alpha_vantage"],
        as_of=as_of,
    )
    primary = _snapshot(snapshot_id=1, component_source="alpha_vantage")
    resolve_bars = [
        _as_of_bar(trading_date=as_of, source="polygon", close="190"),
        _as_of_bar(trading_date=as_of, source="alpha_vantage", close="189.5"),
    ]
    async with _client(
        assessments=[mixed, primary],
        labels=[],
        resolve_bars=resolve_bars,
    ) as client:
        response = await client.get("/research/AAPL/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["latest_assessment_id"] == 3
    assert body["latest_component_source"] == "mixed"
    assert body["latest_input_source"] == "mixed"
    assert body["latest_outcome_label"] is None
    assert body["latest_resolved_label_bar_source"] == "polygon"


async def test_evidence_summary_keeps_mixed_label_bar_source_without_as_of_bars() -> None:
    """Without usable as-of closes, unresolved mixed stays mixed (fail closed)."""

    mixed = _snapshot(
        snapshot_id=2,
        input_source="mixed",
        component_source="mixed",
        coverage_sources=["polygon", "alpha_vantage"],
    )
    async with _client(
        assessments=[mixed],
        labels=[],
        resolve_bars=[
            _as_of_bar(trading_date=date(2024, 1, 25), source="polygon"),
        ],
    ) as client:
        response = await client.get("/research/AAPL/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["latest_resolved_label_bar_source"] == "mixed"


async def test_evidence_summary_counts_mixed_unlabeled() -> None:
    mixed_unlabeled = _snapshot(
        snapshot_id=3,
        input_source="mixed",
        component_source="mixed",
    )
    mixed_labeled = _snapshot(
        snapshot_id=2,
        input_source="mixed",
        component_source="mixed",
    )
    primary = _snapshot(snapshot_id=1, component_source="alpha_vantage")
    labeled = OutcomeLabelData(
        id=11,
        assessment_snapshot_id=2,
        symbol="AAPL",
        label_method_id=LABEL_METHOD_ID,
        label_method_version=1,
        state="research_only",
        as_of_trading_date=date(2024, 1, 26),
        computed_at=datetime(2024, 1, 26, 19, 0, tzinfo=UTC),
        labels={"forward_return_5": 0.04},
        label_end_dates={"forward_return_5": "2024-02-02"},
        schema_version=1,
        bar_source="alpha_vantage",
    )
    async with _client(
        assessments=[mixed_unlabeled, mixed_labeled, primary],
        labels=[labeled],
    ) as client:
        response = await client.get("/research/AAPL/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["mixed_component_source_assessment_count"] == 2
    assert body["mixed_unlabeled_assessment_count"] == 1
    assert body["mixed_labeled_assessment_count"] == 1
    assert body["labeled_assessment_count"] == 1
    assert body["unlabeled_assessment_count"] == 2
    assert body["latest_mixed_label_bar_source"] == "alpha_vantage"
    assert body["latest_resolved_label_bar_source"] == "mixed"
    assert body["latest_outcome_label"] is None
    assert body["most_recent_labeled_assessment_id"] == 2
    assert body["most_recent_labeled_outcome_label"]["labels"]["forward_return_5"] == 0.04
    assert body["most_recent_labeled_outcome_label"]["assessment_snapshot_id"] == 2
    assert body["most_recent_labeled_outcome_label_id"] == 11
    assert body["most_recent_labeled_outcome_label_method_id"] == "forward_total_return_v1"
    assert body["most_recent_labeled_outcome_label_method_version"] == 1
    assert body["most_recent_labeled_outcome_label_schema_version"] == 1
    assert body["most_recent_labeled_outcome_label_state"] == "research_only"
    assert body["most_recent_labeled_outcome_label_bar_source"] == "alpha_vantage"
    assert body["most_recent_labeled_outcome_label_computed_at"] == "2024-01-26T19:00:00Z"
    assert body["most_recent_labeled_outcome_label_as_of_trading_date"] == "2024-01-26"
    assert body["scan_labeled_freshness_lag_trading_days"] == 0
    assert body["latest_outcome_label_id"] is None
    assert body["latest_outcome_label_method_id"] is None

    async with _client(
        assessments=[_snapshot()],
        labels=[_label()],
        calibrations=[_calibration()],
    ) as client:
        response = await client.get("/research/aapl/evidence-summary/export")

    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    disposition = response.headers["content-disposition"]
    assert "attachment" in disposition
    assert 'filename="aegis-AAPL-evidence-summary.json"' in disposition
    body = response.json()
    assert body["symbol"] == "AAPL"
    assert body["state"] == "research_only"
    assert body["latest_assessment"]["id"] == 1
    assert body["latest_assessment"]["probability_confidence"] is None
    assert body["latest_calibration"]["probability_confidence"] == 0.62
    assert body["assessment_count"] == 1


async def test_evidence_summary_export_empty_symbol() -> None:
    readiness = CalibrationReadinessData(
        symbol="MSFT",
        status=CalibrationReadinessStatus.NO_ASSESSMENT,
        assessment_snapshot_id=None,
        research_index=None,
        corpus_count=0,
        bucket_count=0,
        min_corpus=10,
        min_bucket=5,
        index_bucket_width=0.15,
        calibration_method_id=CALIBRATION_METHOD_ID,
        detail="no assessment",
    )
    async with _client(readiness=readiness) as client:
        response = await client.get("/research/MSFT/evidence-summary/export")

    assert response.status_code == 200
    assert 'filename="aegis-MSFT-evidence-summary.json"' in response.headers["content-disposition"]
    body = response.json()
    assert body["state"] == "research_only"
    assert body["latest_assessment"] is None
    assert body["assessment_count"] == 0
    assert body["outcome_label_count"] == 0
    assert body["calibration_count"] == 0


async def test_evidence_summary_export_requires_auth() -> None:
    from aegis.api.dependencies import get_operator_repository, get_session_store

    class _EmptyOperators:
        async def ensure_seeded(self, username: str, password: str) -> None:
            return None

        async def get_by_username(self, username: str) -> None:
            return None

    class _EmptySessions:
        async def get(self, session_id: str) -> None:
            return None

        async def create(self, operator_id: int, username: str) -> str:
            return "unused"

        async def delete(self, session_id: str) -> None:
            return None

    app = create_app(settings=Settings(environment="test", ingestion_schedule_enabled=False))
    app.dependency_overrides[get_operator_repository] = lambda: _EmptyOperators()
    app.dependency_overrides[get_session_store] = lambda: _EmptySessions()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.get("/research/AAPL/evidence-summary/export")
    assert response.status_code == 401
