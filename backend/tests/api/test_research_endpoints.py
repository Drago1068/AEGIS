"""Unit tests for research assessment endpoints via dependency overrides."""

from __future__ import annotations

from datetime import UTC, date, datetime
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient

from aegis.api.dependencies import get_research_assessment_service, require_operator
from aegis.api.main import create_app
from aegis.config.settings import Settings
from aegis.domain.research_assessment import (
    METHOD_ID,
    STATE_RESEARCH_ONLY,
    ResearchAssessmentReason,
    ResearchAssessmentSnapshotData,
    ResearchAssessmentUnavailableError,
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

    async def assess(self, symbol: str) -> ResearchAssessmentSnapshotData:
        self.assess_calls.append(symbol)
        if isinstance(self._on_assess, Exception):
            raise self._on_assess
        assert isinstance(self._on_assess, ResearchAssessmentSnapshotData)
        return self._on_assess

    async def list_assessments(
        self, symbol: str, limit: int
    ) -> list[ResearchAssessmentSnapshotData]:
        return self._listed[:limit]

    async def latest_assessment(
        self, symbol: str
    ) -> ResearchAssessmentSnapshotData | None:
        return self._latest


def _client(
    service: _FakeResearchService,
    *,
    research_outcome_label_after_assessment_enabled: bool = False,
) -> AsyncClient:
    app = create_app(
        settings=Settings(
            environment="test",
            ingestion_schedule_enabled=False,
            research_outcome_label_after_assessment_enabled=(
                research_outcome_label_after_assessment_enabled
            ),
        )
    )
    app.dependency_overrides[require_operator] = _operator
    app.dependency_overrides[get_research_assessment_service] = lambda: service
    if research_outcome_label_after_assessment_enabled:
        app.state.db_session_factory = lambda: _FakeSessionContext()
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


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
    ) as mock_try:
        async with _client(
            research,
            research_outcome_label_after_assessment_enabled=True,
        ) as client:
            response = await client.post("/research/aapl/assessments")

        assert response.status_code == 200
        mock_try.assert_awaited_once()


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
