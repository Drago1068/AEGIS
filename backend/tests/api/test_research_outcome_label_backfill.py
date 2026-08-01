"""API tests for research outcome-label backfill (Phase 43/49)."""

from __future__ import annotations

from datetime import UTC, date, datetime

from httpx import ASGITransport, AsyncClient

from aegis.api.dependencies import (
    get_outcome_label_service,
    get_research_assessment_service,
    require_operator,
)
from aegis.api.main import create_app
from aegis.config.settings import Settings
from aegis.domain.research_assessment import (
    METHOD_ID,
    STATE_RESEARCH_ONLY,
    ResearchAssessmentSnapshotData,
)
from aegis.domain.research_outcome_label_backfill import BACKFILL_SCAN_LIMIT
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


def _snapshot(*, snapshot_id: int) -> ResearchAssessmentSnapshotData:
    return ResearchAssessmentSnapshotData(
        id=snapshot_id,
        symbol="AAPL",
        method_id=METHOD_ID,
        method_version=1,
        state=STATE_RESEARCH_ONLY,
        as_of_trading_date=date(2024, 1, 26),
        event_time=datetime(2024, 1, 26, 23, 59, 59, tzinfo=UTC),
        computed_at=datetime(2024, 1, 26, 18, 0, tzinfo=UTC),
        coverage_confidence=0.95,
        probability_confidence=None,
        components={
            "total_return_20": 0.1,
            "realized_vol_20": 0.2,
            "research_index": 0.46,
        },
        schema_version=1,
        input_source="alpha_vantage",
        lookback_start_date=date(2023, 12, 27),
        lookback_end_date=date(2024, 1, 26),
        bar_count=20,
    )


def _label(*, assessment_id: int = 1) -> OutcomeLabelData:
    return OutcomeLabelData(
        id=10,
        assessment_snapshot_id=assessment_id,
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


class _FakeAssessmentService:
    def __init__(self, listed: list[ResearchAssessmentSnapshotData]) -> None:
        self._listed = listed
        self.list_calls: list[tuple[str, int]] = []

    async def list_assessments(
        self, symbol: str, limit: int
    ) -> list[ResearchAssessmentSnapshotData]:
        self.list_calls.append((symbol, limit))
        return self._listed[:limit]


class _FakeOutcomeLabelService:
    def __init__(
        self,
        *,
        fail_ids: set[int] | None = None,
        selected: list[tuple[str, int]] | None = None,
        ready_selected: list[tuple[str, int]] | None = None,
        ready_fail_ids: set[int] | None = None,
    ) -> None:
        self._fail_ids = fail_ids or set()
        self._selected = selected
        self._ready_selected = ready_selected
        self._ready_fail_ids = ready_fail_ids or set()
        self.label_calls: list[tuple[str, int]] = []
        self.ready_horizon_calls: list[tuple[str, int]] = []
        self.select_calls: list[tuple[str, int, int]] = []
        self.ready_select_calls: list[tuple[str, int, int]] = []

    async def select_backfill_candidates(
        self,
        symbol: str,
        snapshots: list[ResearchAssessmentSnapshotData],
        limit: int,
    ) -> list[tuple[str, int]]:
        self.select_calls.append((symbol, len(snapshots), limit))
        if self._selected is not None:
            return self._selected[:limit]
        pairs: list[tuple[str, int]] = []
        for snapshot in snapshots:
            if snapshot.id is not None:
                pairs.append((snapshot.symbol, snapshot.id))
            if len(pairs) >= limit:
                break
        return pairs

    async def select_ready_horizons_backfill_candidates(
        self,
        symbol: str,
        snapshots: list[ResearchAssessmentSnapshotData],
        limit: int,
    ) -> list[tuple[str, int]]:
        self.ready_select_calls.append((symbol, len(snapshots), limit))
        if self._ready_selected is not None:
            return self._ready_selected[:limit]
        pairs: list[tuple[str, int]] = []
        for snapshot in snapshots:
            if snapshot.id is not None:
                pairs.append((snapshot.symbol, snapshot.id))
            if len(pairs) >= limit:
                break
        return pairs

    async def label_assessment(self, symbol: str, assessment_id: int) -> OutcomeLabelData:
        self.label_calls.append((symbol, assessment_id))
        if assessment_id in self._fail_ids:
            raise OutcomeLabelUnavailableError(
                OutcomeLabelReason.INSUFFICIENT_FORWARD_BARS,
                "need more bars",
            )
        return _label(assessment_id=assessment_id)

    async def label_assessment_ready_horizons(
        self, symbol: str, assessment_id: int
    ) -> OutcomeLabelData:
        self.ready_horizon_calls.append((symbol, assessment_id))
        if assessment_id in self._ready_fail_ids:
            raise OutcomeLabelUnavailableError(
                OutcomeLabelReason.INSUFFICIENT_FORWARD_BARS,
                "no ready horizons",
            )
        return OutcomeLabelData(
            id=11,
            assessment_snapshot_id=assessment_id,
            symbol="AAPL",
            label_method_id=LABEL_METHOD_ID,
            label_method_version=1,
            state="research_only",
            as_of_trading_date=date(2024, 1, 2),
            computed_at=datetime(2024, 1, 10, 12, tzinfo=UTC),
            labels={"forward_return_5": 0.05},
            label_end_dates={"forward_return_5": "2024-01-09"},
            schema_version=1,
            bar_source="alpha_vantage",
        )


def _client(
    assessment_service: _FakeAssessmentService,
    label_service: _FakeOutcomeLabelService,
) -> AsyncClient:
    app = create_app(settings=Settings(environment="test", ingestion_schedule_enabled=False))
    app.dependency_overrides[require_operator] = _operator
    app.dependency_overrides[get_research_assessment_service] = lambda: assessment_service
    app.dependency_overrides[get_outcome_label_service] = lambda: label_service
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


async def test_backfill_persists_and_skips_fail_closed() -> None:
    assessment_service = _FakeAssessmentService(
        [_snapshot(snapshot_id=2), _snapshot(snapshot_id=1)]
    )
    label_service = _FakeOutcomeLabelService(fail_ids={1})

    async with _client(assessment_service, label_service) as client:
        response = await client.post("/research/AAPL/outcome-labels/backfill?limit=20")

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "AAPL"
    assert body["assessment_count"] == 2
    assert body["persisted_count"] == 1
    assert body["skipped_count"] == 1
    assert body["outcomes"][0]["assessment_snapshot_id"] == 2
    assert body["outcomes"][0]["persisted"] is True
    assert body["outcomes"][1]["assessment_snapshot_id"] == 1
    assert body["outcomes"][1]["persisted"] is False
    assert body["outcomes"][1]["reason"] == "insufficient_forward_bars"
    assert "not advice" in body["detail"]
    assert assessment_service.list_calls == [("AAPL", BACKFILL_SCAN_LIMIT)]
    assert label_service.select_calls == [("AAPL", 2, 20)]
    assert label_service.label_calls == [("AAPL", 2), ("AAPL", 1)]


async def test_backfill_uses_selected_unlabeled_candidates_only() -> None:
    assessment_service = _FakeAssessmentService(
        [_snapshot(snapshot_id=3), _snapshot(snapshot_id=2), _snapshot(snapshot_id=1)]
    )
    label_service = _FakeOutcomeLabelService(selected=[("AAPL", 1)])

    async with _client(assessment_service, label_service) as client:
        response = await client.post("/research/AAPL/outcome-labels/backfill?limit=20")

    assert response.status_code == 200
    body = response.json()
    assert body["assessment_count"] == 1
    assert body["persisted_count"] == 1
    assert label_service.label_calls == [("AAPL", 1)]


async def test_backfill_empty_history_returns_zero_counts() -> None:
    assessment_service = _FakeAssessmentService([])
    label_service = _FakeOutcomeLabelService()

    async with _client(assessment_service, label_service) as client:
        response = await client.post("/research/aapl/outcome-labels/backfill")

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "AAPL"
    assert body["assessment_count"] == 0
    assert body["persisted_count"] == 0
    assert body["skipped_count"] == 0
    assert body["outcomes"] == []
    assert label_service.label_calls == []
    assert assessment_service.list_calls == [("aapl", BACKFILL_SCAN_LIMIT)]
    assert label_service.select_calls == [("aapl", 0, 100)]
    assert BACKFILL_SCAN_LIMIT == 252


async def test_ready_horizons_backfill_persists_and_skips_fail_closed() -> None:
    assessment_service = _FakeAssessmentService(
        [_snapshot(snapshot_id=2), _snapshot(snapshot_id=1)]
    )
    label_service = _FakeOutcomeLabelService(ready_fail_ids={1})

    async with _client(assessment_service, label_service) as client:
        response = await client.post(
            "/research/AAPL/outcome-labels/backfill/ready-horizons?limit=20"
        )

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "AAPL"
    assert body["assessment_count"] == 2
    assert body["persisted_count"] == 1
    assert body["skipped_count"] == 1
    assert body["outcomes"][0]["persisted"] is True
    assert body["outcomes"][1]["persisted"] is False
    assert body["outcomes"][1]["reason"] == "insufficient_forward_bars"
    assert "ready-horizons" in body["detail"]
    assert assessment_service.list_calls == [("AAPL", BACKFILL_SCAN_LIMIT)]
    assert label_service.ready_select_calls == [("AAPL", 2, 20)]
    assert label_service.ready_horizon_calls == [("AAPL", 2), ("AAPL", 1)]
    assert label_service.label_calls == []


async def test_ready_horizons_backfill_uses_selected_candidates_only() -> None:
    assessment_service = _FakeAssessmentService(
        [_snapshot(snapshot_id=3), _snapshot(snapshot_id=2), _snapshot(snapshot_id=1)]
    )
    label_service = _FakeOutcomeLabelService(ready_selected=[("AAPL", 1)])

    async with _client(assessment_service, label_service) as client:
        response = await client.post(
            "/research/AAPL/outcome-labels/backfill/ready-horizons?limit=20"
        )

    assert response.status_code == 200
    body = response.json()
    assert body["assessment_count"] == 1
    assert body["persisted_count"] == 1
    assert label_service.ready_horizon_calls == [("AAPL", 1)]
    assert label_service.label_calls == []
