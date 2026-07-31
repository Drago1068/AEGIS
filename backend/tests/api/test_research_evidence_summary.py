"""API tests for research evidence summary (Phase 22, ADR-0023)."""

from __future__ import annotations

from datetime import UTC, date, datetime

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
from aegis.domain.research_assessment import ResearchAssessmentSnapshotData
from aegis.domain.research_outcome_labels import LABEL_METHOD_ID, OutcomeLabelData
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
) -> ResearchAssessmentSnapshotData:
    components: dict[str, float | str] = {"research_index": 0.46}
    if component_source is not None:
        components["component_source"] = component_source
    return ResearchAssessmentSnapshotData(
        id=snapshot_id,
        symbol="AAPL",
        method_id="daily_bar_research_v1",
        method_version=1,
        state="research_only",
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


def _label() -> OutcomeLabelData:
    return OutcomeLabelData(
        id=10,
        assessment_snapshot_id=1,
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
    def __init__(self, listed: list[OutcomeLabelData] | None = None) -> None:
        self._listed = listed or []

    async def list_labels_for_assessment(
        self, symbol: str, assessment_snapshot_id: int, limit: int
    ) -> list[OutcomeLabelData]:
        matched = [
            row
            for row in self._listed
            if row.assessment_snapshot_id == assessment_snapshot_id
        ]
        return matched[:limit]

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
) -> AsyncClient:
    app = create_app(settings=Settings(environment="test", ingestion_schedule_enabled=False))
    app.dependency_overrides[require_operator] = _operator
    app.dependency_overrides[get_research_assessment_service] = lambda: _FakeAssessmentService(
        assessments
    )
    app.dependency_overrides[get_outcome_label_service] = lambda: _FakeOutcomeLabelService(labels)
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
    ) as client:
        response = await client.get("/research/aapl/evidence-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "AAPL"
    assert body["latest_assessment"]["id"] == 1
    assert body["latest_assessment"]["probability_confidence"] is None
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
    assert body["latest_outcome_label_id"] == 10


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
    assert body["latest_outcome_label"] is None
    assert body["most_recent_labeled_assessment_id"] == 2
    assert body["most_recent_labeled_outcome_label"]["labels"]["forward_return_5"] == 0.04
    assert body["most_recent_labeled_outcome_label"]["assessment_snapshot_id"] == 2
    assert body["most_recent_labeled_outcome_label_id"] == 11
    assert body["most_recent_labeled_outcome_label_method_id"] == "forward_total_return_v1"
    assert body["most_recent_labeled_outcome_label_method_version"] == 1
    assert body["most_recent_labeled_outcome_label_schema_version"] == 1
    assert body["most_recent_labeled_outcome_label_state"] == "research_only"
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
