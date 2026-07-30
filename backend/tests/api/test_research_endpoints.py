"""Unit tests for research assessment endpoints via dependency overrides."""

from __future__ import annotations

from datetime import UTC, date, datetime
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient

from aegis.api.dependencies import (
    get_research_assessment_service,
    get_research_calibration_repository,
    get_research_calibration_service,
    require_operator,
)
from aegis.api.main import create_app
from aegis.config.settings import Settings
from aegis.domain.research_assessment import (
    METHOD_ID,
    STATE_RESEARCH_ONLY,
    ResearchAssessmentReason,
    ResearchAssessmentSnapshotData,
    ResearchAssessmentUnavailableError,
)
from aegis.domain.research_probability_calibration import (
    CALIBRATION_METHOD_ID,
    CalibrationReadinessData,
    CalibrationReadinessStatus,
)
from aegis.persistence.models import Operator


class _FakeSessionContext:
    async def __aenter__(self) -> object:
        return object()

    async def __aexit__(self, *args: object) -> None:
        return None


def _operator() -> Operator:
    return Operator(
        id=1,
        username="operator",
        password_hash="unused-in-override",
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
        updated_at=datetime(2024, 1, 1, tzinfo=UTC),
    )


def _snapshot(**overrides: object) -> ResearchAssessmentSnapshotData:
    defaults: dict[str, object] = {
        "id": 99,
        "symbol": "AAPL",
        "method_id": METHOD_ID,
        "method_version": 1,
        "state": STATE_RESEARCH_ONLY,
        "as_of_trading_date": date(2024, 1, 26),
        "event_time": datetime(2024, 1, 26, 23, 59, 59, tzinfo=UTC),
        "computed_at": datetime(2024, 1, 26, 18, 0, tzinfo=UTC),
        "coverage_confidence": 0.95,
        "probability_confidence": None,
        "components": {
            "total_return_20": 0.1,
            "realized_vol_20": 0.2,
            "research_index": 0.46,
        },
        "schema_version": 1,
        "input_source": "alpha_vantage",
        "lookback_start_date": date(2023, 12, 27),
        "lookback_end_date": date(2024, 1, 26),
        "bar_count": 20,
    }
    defaults.update(overrides)
    return ResearchAssessmentSnapshotData(**defaults)  # type: ignore[arg-type]


class _FakeResearchService:
    def __init__(
        self,
        *,
        on_assess: ResearchAssessmentSnapshotData | Exception | None = None,
        listed: list[ResearchAssessmentSnapshotData] | None = None,
        latest: ResearchAssessmentSnapshotData | None = None,
    ) -> None:
        self._on_assess = on_assess
        self._listed = listed or []
        self._latest = latest
        self.assess_calls: list[str] = []
        self.list_calls: list[tuple[str, int]] = []

    async def assess(self, symbol: str) -> ResearchAssessmentSnapshotData:
        self.assess_calls.append(symbol)
        if isinstance(self._on_assess, Exception):
            raise self._on_assess
        assert isinstance(self._on_assess, ResearchAssessmentSnapshotData)
        return self._on_assess

    async def list_assessments(
        self, symbol: str, limit: int
    ) -> list[ResearchAssessmentSnapshotData]:
        self.list_calls.append((symbol, limit))
        return self._listed[:limit]

    async def latest_assessment(
        self, symbol: str
    ) -> ResearchAssessmentSnapshotData | None:
        return self._latest


class _FakeCalibrationRepository:
    async def get_latest_for_assessment(self, assessment_snapshot_id: int) -> None:
        return None


class _FakeCalibrationService:
    def __init__(self, readiness: CalibrationReadinessData) -> None:
        self._readiness = readiness
        self.evaluate_calls: list[str] = []

    async def evaluate_readiness(
        self,
        symbol: str,
        snapshot: ResearchAssessmentSnapshotData | None,
    ) -> CalibrationReadinessData:
        self.evaluate_calls.append(symbol.upper())
        return self._readiness


def _client(
    service: _FakeResearchService,
    *,
    research_outcome_label_after_assessment_enabled: bool = False,
    research_calibration_after_label_enabled: bool = False,
    calibration_service: _FakeCalibrationService | None = None,
) -> AsyncClient:
    app = create_app(
        settings=Settings(
            environment="test",
            ingestion_schedule_enabled=False,
            research_outcome_label_after_assessment_enabled=(
                research_outcome_label_after_assessment_enabled
            ),
            research_calibration_after_label_enabled=research_calibration_after_label_enabled,
        )
    )
    app.dependency_overrides[require_operator] = _operator
    app.dependency_overrides[get_research_assessment_service] = lambda: service
    app.dependency_overrides[get_research_calibration_repository] = (
        lambda: _FakeCalibrationRepository()
    )
    if calibration_service is not None:
        app.dependency_overrides[get_research_calibration_service] = lambda: calibration_service
    if research_outcome_label_after_assessment_enabled or research_calibration_after_label_enabled:
        app.state.db_session_factory = lambda: _FakeSessionContext()
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


async def test_get_calibration_readiness_returns_payload() -> None:
    snap = _snapshot()
    research = _FakeResearchService(latest=snap)
    readiness = CalibrationReadinessData(
        symbol="AAPL",
        status=CalibrationReadinessStatus.INSUFFICIENT_LABELED_CORPUS,
        assessment_snapshot_id=99,
        research_index=0.46,
        corpus_count=3,
        bucket_count=2,
        min_corpus=10,
        min_bucket=5,
        index_bucket_width=0.15,
        calibration_method_id=CALIBRATION_METHOD_ID,
        detail="need at least 10 labeled historical examples, found 3",
    )
    calibration = _FakeCalibrationService(readiness)

    async with _client(research, calibration_service=calibration) as client:
        response = await client.get("/research/aapl/calibration-readiness")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "insufficient_labeled_corpus"
    assert body["corpus_count"] == 3
    assert body["bucket_count"] == 2
    assert body["calibration_method_id"] == CALIBRATION_METHOD_ID
    assert calibration.evaluate_calls == ["AAPL"]


async def test_export_calibration_readiness_attachment() -> None:
    snap = _snapshot()
    research = _FakeResearchService(latest=snap)
    readiness = CalibrationReadinessData(
        symbol="AAPL",
        status=CalibrationReadinessStatus.INSUFFICIENT_LABELED_CORPUS,
        assessment_snapshot_id=99,
        research_index=0.46,
        corpus_count=3,
        bucket_count=2,
        min_corpus=10,
        min_bucket=5,
        index_bucket_width=0.15,
        calibration_method_id=CALIBRATION_METHOD_ID,
        detail="need at least 10 labeled historical examples, found 3",
    )
    calibration = _FakeCalibrationService(readiness)

    async with _client(research, calibration_service=calibration) as client:
        response = await client.get("/research/aapl/calibration-readiness/export")

    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    disposition = response.headers["content-disposition"]
    assert "attachment" in disposition
    assert 'filename="aegis-AAPL-calibration-readiness.json"' in disposition
    body = response.json()
    assert body["status"] == "insufficient_labeled_corpus"
    assert body["corpus_count"] == 3
    assert body["symbol"] == "AAPL"
    assert calibration.evaluate_calls == ["AAPL"]


async def test_export_calibration_readiness_requires_auth() -> None:
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
        response = await client.get("/research/AAPL/calibration-readiness/export")
    assert response.status_code == 401


async def test_post_assessment_returns_research_only_payload() -> None:
    snap = _snapshot()
    service = _FakeResearchService(on_assess=snap)

    async with _client(service) as client:
        response = await client.post("/research/aapl/assessments")

    assert response.status_code == 200
    body = response.json()
    assert body["state"] == "research_only"
    assert body["probability_confidence"] is None
    assert body["coverage_confidence"] == 0.95
    assert body["method_id"] == METHOD_ID
    assert service.assess_calls == ["aapl"]


async def test_post_assessment_triggers_outcome_labels_when_flag_enabled() -> None:
    snap = _snapshot()
    research = _FakeResearchService(on_assess=snap)

    with patch(
        "aegis.api.routers.research.build_outcome_label_service",
        return_value=object(),
    ), patch(
        "aegis.api.routers.research.try_label_assessment_after_create",
        new_callable=AsyncMock,
    ) as mock_try, patch(
        "aegis.api.routers.research.enrich_assessment_with_calibration",
        new_callable=AsyncMock,
    ) as mock_enrich:
        async def _passthrough(
            snapshot: ResearchAssessmentSnapshotData,
            _repo: object,
        ) -> ResearchAssessmentSnapshotData:
            return snapshot

        mock_enrich.side_effect = _passthrough
        async with _client(
            research,
            research_outcome_label_after_assessment_enabled=True,
        ) as client:
            response = await client.post("/research/aapl/assessments")

        assert response.status_code == 200
        mock_try.assert_awaited_once()


async def test_post_assessment_triggers_calibration_when_flag_enabled() -> None:
    snap = _snapshot()
    research = _FakeResearchService(on_assess=snap)

    with patch(
        "aegis.api.routers.research.build_research_calibration_service",
        return_value=object(),
    ), patch(
        "aegis.api.routers.research.try_calibrate_assessment_after_create",
        new_callable=AsyncMock,
    ) as mock_calibrate, patch(
        "aegis.api.routers.research.enrich_assessment_with_calibration",
        new_callable=AsyncMock,
    ) as mock_enrich:
        async def _passthrough(
            snapshot: ResearchAssessmentSnapshotData,
            _repo: object,
        ) -> ResearchAssessmentSnapshotData:
            return snapshot

        mock_enrich.side_effect = _passthrough
        async with _client(
            research,
            research_calibration_after_label_enabled=True,
        ) as client:
            response = await client.post("/research/aapl/assessments")

        assert response.status_code == 200
        mock_calibrate.assert_awaited_once()


async def test_post_assessment_skips_outcome_labels_when_flag_disabled() -> None:
    snap = _snapshot()
    research = _FakeResearchService(on_assess=snap)

    with patch(
        "aegis.api.routers.research.try_label_assessment_after_create",
        new_callable=AsyncMock,
    ) as mock_try:
        async with _client(
            research,
            research_outcome_label_after_assessment_enabled=False,
        ) as client:
            response = await client.post("/research/aapl/assessments")

        assert response.status_code == 200
        mock_try.assert_not_awaited()


async def test_post_assessment_fail_closed_returns_422_and_reason() -> None:
    service = _FakeResearchService(
        on_assess=ResearchAssessmentUnavailableError(
            ResearchAssessmentReason.INSUFFICIENT_PRIMARY_BARS,
            "need 20 usable primary bars, found 5",
        )
    )

    async with _client(service) as client:
        response = await client.post("/research/AAPL/assessments")

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["reason"] == "insufficient_primary_bars"
    assert "need 20" in detail["message"]


async def test_list_assessments_newest_first() -> None:
    older = _snapshot(computed_at=datetime(2024, 1, 20, tzinfo=UTC))
    newer = _snapshot(computed_at=datetime(2024, 1, 26, tzinfo=UTC))
    service = _FakeResearchService(listed=[newer, older])

    async with _client(service) as client:
        response = await client.get("/research/AAPL/assessments")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["computed_at"] > body[1]["computed_at"]


async def test_export_assessments_attachment() -> None:
    older = _snapshot(id=98, computed_at=datetime(2024, 1, 20, tzinfo=UTC))
    newer = _snapshot(id=99, computed_at=datetime(2024, 1, 26, tzinfo=UTC))
    service = _FakeResearchService(listed=[newer, older])

    async with _client(service) as client:
        response = await client.get("/research/aapl/assessments/export?limit=10")

    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    disposition = response.headers["content-disposition"]
    assert "attachment" in disposition
    assert 'filename="aegis-AAPL-assessments.json"' in disposition
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2
    assert body[0]["id"] == 99
    assert body[0]["state"] == STATE_RESEARCH_ONLY
    assert body[0]["probability_confidence"] is None
    assert service.list_calls == [("aapl", 10)]


async def test_export_assessments_empty_array() -> None:
    service = _FakeResearchService(listed=[])

    async with _client(service) as client:
        response = await client.get("/research/AAPL/assessments/export")

    assert response.status_code == 200
    assert response.json() == []
    assert "attachment" in response.headers["content-disposition"]


async def test_export_assessments_requires_auth() -> None:
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
        response = await client.get("/research/AAPL/assessments/export")
    assert response.status_code == 401


async def test_latest_returns_404_when_missing() -> None:
    service = _FakeResearchService(latest=None)

    async with _client(service) as client:
        response = await client.get("/research/AAPL/assessments/latest")

    assert response.status_code == 404


async def test_latest_returns_snapshot() -> None:
    snap = _snapshot()
    service = _FakeResearchService(latest=snap)

    async with _client(service) as client:
        response = await client.get("/research/AAPL/assessments/latest")

    assert response.status_code == 200
    assert response.json()["symbol"] == "AAPL"


async def test_research_returns_401_without_auth_override() -> None:
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
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/research/AAPL/assessments")

    assert response.status_code == 401
