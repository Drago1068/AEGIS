"""API tests for research assessment backfill (Phase 45, ADR-0046)."""

from __future__ import annotations

from datetime import UTC, date, datetime

from httpx import ASGITransport, AsyncClient

from aegis.api.dependencies import get_research_assessment_service, require_operator
from aegis.api.main import create_app
from aegis.config.settings import Settings
from aegis.domain.research_assessment_backfill import (
    AssessmentBackfillOutcome,
    AssessmentBackfillSummary,
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


class _FakeAssessmentService:
    def __init__(self, summary: AssessmentBackfillSummary) -> None:
        self._summary = summary
        self.backfill_calls: list[tuple[str, int]] = []

    async def backfill_assessments(
        self, symbol: str, limit: int
    ) -> AssessmentBackfillSummary:
        self.backfill_calls.append((symbol, limit))
        return self._summary


def _client(service: _FakeAssessmentService) -> AsyncClient:
    app = create_app(settings=Settings(environment="test", ingestion_schedule_enabled=False))
    app.dependency_overrides[require_operator] = _operator
    app.dependency_overrides[get_research_assessment_service] = lambda: service
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


async def test_backfill_assessments_returns_summary() -> None:
    summary = AssessmentBackfillSummary(
        outcomes=(
            AssessmentBackfillOutcome(
                symbol="AAPL",
                as_of_trading_date=date(2024, 1, 26),
                persisted=False,
                reason="assessment_already_exists",
                detail="exists",
            ),
            AssessmentBackfillOutcome(
                symbol="AAPL",
                as_of_trading_date=date(2024, 1, 25),
                persisted=True,
                assessment_snapshot_id=2,
            ),
        )
    )
    service = _FakeAssessmentService(summary)

    async with _client(service) as client:
        response = await client.post("/research/AAPL/assessments/backfill?limit=20")

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "AAPL"
    assert body["candidate_count"] == 2
    assert body["persisted_count"] == 1
    assert body["skipped_count"] == 1
    assert body["outcomes"][1]["assessment_snapshot_id"] == 2
    assert "not advice" in body["detail"]
    assert service.backfill_calls == [("AAPL", 20)]


async def test_backfill_assessments_empty_candidates() -> None:
    service = _FakeAssessmentService(AssessmentBackfillSummary(outcomes=()))

    async with _client(service) as client:
        response = await client.post("/research/aapl/assessments/backfill")

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "AAPL"
    assert body["candidate_count"] == 0
    assert body["outcomes"] == []
