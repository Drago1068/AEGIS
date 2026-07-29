"""API tests for research outcome label endpoints."""

from __future__ import annotations

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
        latest: OutcomeLabelData | None = None,
    ) -> None:
        self._on_label = on_label
        self._latest = latest
        self.label_calls: list[tuple[str, int]] = []

    async def label_assessment(self, symbol: str, assessment_id: int) -> OutcomeLabelData:
        self.label_calls.append((symbol, assessment_id))
        if isinstance(self._on_label, Exception):
            raise self._on_label
        assert isinstance(self._on_label, OutcomeLabelData)
        return self._on_label

    async def latest_label_for_assessment(
        self, assessment_snapshot_id: int
    ) -> OutcomeLabelData | None:
        return self._latest


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


async def test_get_latest_outcome_labels() -> None:
    label = _label()
    service = _FakeOutcomeLabelService(latest=label)

    async with _client(service) as client:
        response = await client.get("/research/AAPL/assessments/1/outcome-labels/latest")

    assert response.status_code == 200
    assert response.json()["assessment_snapshot_id"] == 1
