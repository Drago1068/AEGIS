"""API tests for research outcome label endpoints (Phase 13/20)."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime

from httpx import ASGITransport, AsyncClient

from aegis.api.dependencies import get_outcome_label_service, require_operator
from aegis.api.main import create_app
from aegis.config.settings import Settings
from aegis.domain.research_outcome_labels import (
    LABEL_METHOD_ID,
    OutcomeLabelData,
    OutcomeLabelReason,
    OutcomeLabelUnavailableError,
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


def _label() -> OutcomeLabelData:
    return OutcomeLabelData(
        id=10,
        assessment_snapshot_id=1,
        symbol="AAPL",
        label_method_id=LABEL_METHOD_ID,
        label_method_version=1,
        state="research_only",
        as_of_trading_date=date(2024, 1, 2),
        computed_at=datetime(2024, 1, 10, 12, tzinfo=UTC),
        labels={"forward_return_5": 0.05, "forward_return_20": 0.1},
        label_end_dates={
            "forward_return_5": "2024-01-09",
            "forward_return_20": "2024-02-01",
        },
        schema_version=1,
        bar_source="alpha_vantage",
    )


class _FakeOutcomeLabelService:
    def __init__(
        self,
        *,
        on_label: OutcomeLabelData | Exception | None = None,
        on_ready_horizons: OutcomeLabelData | Exception | None = None,
        latest: OutcomeLabelData | None = None,
        listed: list[OutcomeLabelData] | None = None,
    ) -> None:
        self._on_label = on_label
        self._on_ready_horizons = on_ready_horizons
        self._latest = latest
        self._listed = listed or []
        self.label_calls: list[tuple[str, int]] = []
        self.ready_horizon_calls: list[tuple[str, int]] = []
        self.list_calls: list[tuple[str, int, int]] = []

    async def label_assessment(self, symbol: str, assessment_id: int) -> OutcomeLabelData:
        self.label_calls.append((symbol, assessment_id))
        if isinstance(self._on_label, Exception):
            raise self._on_label
        assert isinstance(self._on_label, OutcomeLabelData)
        return self._on_label

    async def label_assessment_ready_horizons(
        self, symbol: str, assessment_id: int
    ) -> OutcomeLabelData:
        self.ready_horizon_calls.append((symbol, assessment_id))
        payload = self._on_ready_horizons if self._on_ready_horizons is not None else self._on_label
        if isinstance(payload, Exception):
            raise payload
        assert isinstance(payload, OutcomeLabelData)
        return payload

    async def latest_label_for_assessment(
        self, assessment_snapshot_id: int
    ) -> OutcomeLabelData | None:
        return self._latest

    async def list_labels_for_assessment(
        self,
        symbol: str,
        assessment_snapshot_id: int,
        limit: int,
    ) -> list[OutcomeLabelData]:
        self.list_calls.append((symbol, assessment_snapshot_id, limit))
        return self._listed[:limit]


def _client(service: _FakeOutcomeLabelService) -> AsyncClient:
    app = create_app(settings=Settings(environment="test", ingestion_schedule_enabled=False))
    app.dependency_overrides[require_operator] = _operator
    app.dependency_overrides[get_outcome_label_service] = lambda: service
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


async def test_post_outcome_labels_returns_payload() -> None:
    label = _label()
    service = _FakeOutcomeLabelService(on_label=label)

    async with _client(service) as client:
        response = await client.post("/research/AAPL/assessments/1/outcome-labels")

    assert response.status_code == 200
    body = response.json()
    assert body["label_method_id"] == LABEL_METHOD_ID
    assert body["labels"]["forward_return_5"] == 0.05
    assert service.label_calls == [("AAPL", 1)]


async def test_post_outcome_labels_422_on_fail_closed() -> None:
    service = _FakeOutcomeLabelService(
        on_label=OutcomeLabelUnavailableError(
            OutcomeLabelReason.INSUFFICIENT_FORWARD_BARS,
            "need more bars",
        )
    )

    async with _client(service) as client:
        response = await client.post("/research/AAPL/assessments/1/outcome-labels")

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["reason"] == "insufficient_forward_bars"


async def test_post_outcome_labels_ready_horizons_returns_partial_payload() -> None:
    partial = replace(
        _label(),
        labels={"forward_return_5": 0.05},
        label_end_dates={"forward_return_5": "2024-01-09"},
    )
    service = _FakeOutcomeLabelService(on_ready_horizons=partial)

    async with _client(service) as client:
        response = await client.post(
            "/research/AAPL/assessments/1/outcome-labels/ready-horizons"
        )

    assert response.status_code == 200
    body = response.json()
    assert body["labels"] == {"forward_return_5": 0.05}
    assert "forward_return_20" not in body["labels"]
    assert service.ready_horizon_calls == [("AAPL", 1)]
    assert service.label_calls == []


async def test_post_outcome_labels_ready_horizons_422_when_none_ready() -> None:
    service = _FakeOutcomeLabelService(
        on_ready_horizons=OutcomeLabelUnavailableError(
            OutcomeLabelReason.INSUFFICIENT_FORWARD_BARS,
            "no configured forward horizons are label-ready",
        )
    )

    async with _client(service) as client:
        response = await client.post(
            "/research/AAPL/assessments/1/outcome-labels/ready-horizons"
        )

    assert response.status_code == 422
    assert response.json()["detail"]["reason"] == "insufficient_forward_bars"


async def test_get_latest_outcome_labels() -> None:
    label = _label()
    service = _FakeOutcomeLabelService(latest=label)

    async with _client(service) as client:
        response = await client.get("/research/AAPL/assessments/1/outcome-labels/latest")

    assert response.status_code == 200
    assert response.json()["assessment_snapshot_id"] == 1


async def test_list_outcome_labels_newest_first() -> None:
    newer = _label()
    older = replace(
        newer,
        id=9,
        computed_at=datetime(2024, 1, 9, 12, tzinfo=UTC),
        labels={"forward_return_5": 0.04, "forward_return_20": 0.08},
    )
    service = _FakeOutcomeLabelService(listed=[newer, older])

    async with _client(service) as client:
        response = await client.get("/research/AAPL/assessments/1/outcome-labels?limit=10")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["id"] == 10
    assert body[1]["id"] == 9
    assert body[0]["state"] == "research_only"
    assert service.list_calls == [("AAPL", 1, 10)]


async def test_list_outcome_labels_empty() -> None:
    service = _FakeOutcomeLabelService(listed=[])

    async with _client(service) as client:
        response = await client.get("/research/AAPL/assessments/1/outcome-labels")

    assert response.status_code == 200
    assert response.json() == []


async def test_export_outcome_labels_attachment() -> None:
    newer = _label()
    older = replace(
        newer,
        id=9,
        computed_at=datetime(2024, 1, 9, 12, tzinfo=UTC),
        labels={"forward_return_5": 0.04, "forward_return_20": 0.08},
    )
    service = _FakeOutcomeLabelService(listed=[newer, older])

    async with _client(service) as client:
        response = await client.get(
            "/research/aapl/assessments/1/outcome-labels/export?limit=10"
        )

    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    disposition = response.headers["content-disposition"]
    assert "attachment" in disposition
    assert 'filename="aegis-AAPL-assessment-1-outcome-labels.json"' in disposition
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2
    assert body[0]["id"] == 10
    assert body[0]["labels"]["forward_return_5"] == 0.05
    assert service.list_calls == [("aapl", 1, 10)]


async def test_export_outcome_labels_empty_array() -> None:
    service = _FakeOutcomeLabelService(listed=[])

    async with _client(service) as client:
        response = await client.get("/research/AAPL/assessments/1/outcome-labels/export")

    assert response.status_code == 200
    assert response.json() == []
    assert "attachment" in response.headers["content-disposition"]


async def test_export_outcome_labels_requires_auth() -> None:
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
        response = await client.get("/research/AAPL/assessments/1/outcome-labels/export")
    assert response.status_code == 401
