"""Unit tests for the market data ingest/read endpoints, via dependency overrides.

No real network or database access: both endpoints are exercised entirely through fake
doubles substituted with ``app.dependency_overrides``. Operator auth is bypassed via an
override of ``require_operator`` (see Phase 4 / ADR-0005).
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient

from aegis.api.dependencies import (
    get_active_watchlist_symbols,
    get_ingestion_service,
    get_market_data_repository,
    get_research_assessment_service,
    require_operator,
)
from aegis.api.main import create_app
from aegis.config.settings import Settings
from aegis.domain.market_data_ingestion import IngestionRunResult, SymbolIngestionResult
from aegis.domain.market_data_validation import RejectionReason
from aegis.domain.research_assessment import (
    METHOD_ID,
    STATE_RESEARCH_ONLY,
    ResearchAssessmentSnapshotData,
)
from aegis.persistence.models import MarketDailyBarObservation, Operator


def _operator() -> Operator:
    return Operator(
        id=1,
        username="operator",
        password_hash="unused-in-override",
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
        updated_at=datetime(2024, 1, 1, tzinfo=UTC),
    )


class _FakeIngestionService:
    def __init__(self, result: IngestionRunResult) -> None:
        self._result = result
        self.requested_symbols: list[str] | None = None

    async def run(self, symbols: list[str]) -> IngestionRunResult:
        self.requested_symbols = symbols
        return self._result


class _FakeRepository:
    def __init__(self, bars: list[MarketDailyBarObservation]) -> None:
        self._bars = bars

    async def list_recent(self, symbol: str, limit: int) -> list[MarketDailyBarObservation]:
        return self._bars[:limit]


def _bar(symbol: str = "AAPL") -> MarketDailyBarObservation:
    return MarketDailyBarObservation(
        id=1,
        source="alpha_vantage",
        symbol=symbol,
        trading_date=date(2024, 1, 2),
        event_time=datetime(2024, 1, 2, tzinfo=UTC),
        ingested_at=datetime(2024, 1, 2, 12, tzinfo=UTC),
        open=Decimal("100"),
        high=Decimal("110"),
        low=Decimal("90"),
        close=Decimal("105"),
        volume=1000,
        data_quality="primary",
        schema_version=1,
        raw_payload={},
        observation_kind="initial",
        supersedes_observation_id=None,
    )


class _FakeResearchService:
    def __init__(self) -> None:
        self.assess_calls: list[str] = []

    async def assess(self, symbol: str) -> ResearchAssessmentSnapshotData:
        self.assess_calls.append(symbol)
        return ResearchAssessmentSnapshotData(
            id=7,
            symbol=symbol,
            method_id=METHOD_ID,
            method_version=1,
            state=STATE_RESEARCH_ONLY,
            as_of_trading_date=date(2024, 1, 26),
            event_time=datetime(2024, 1, 26, 23, 59, 59, tzinfo=UTC),
            computed_at=datetime(2024, 1, 26, 18, 0, tzinfo=UTC),
            coverage_confidence=0.9,
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


class _FakeSessionContext:
    async def __aenter__(self) -> object:
        return object()

    async def __aexit__(self, *args: object) -> None:
        return None


def _client_with_overrides(
    *,
    ingestion_service: _FakeIngestionService | None = None,
    repository: _FakeRepository | None = None,
    research_service: _FakeResearchService | None = None,
    research_schedule_after_ingest_enabled: bool = False,
    research_outcome_label_after_assessment_enabled: bool = False,
) -> AsyncClient:
    app = create_app(
        settings=Settings(
            environment="test",
            ingestion_schedule_enabled=False,
            research_schedule_after_ingest_enabled=research_schedule_after_ingest_enabled,
            research_outcome_label_after_assessment_enabled=(
                research_outcome_label_after_assessment_enabled
            ),
        )
    )
    app.dependency_overrides[require_operator] = _operator
    if ingestion_service is not None:
        app.dependency_overrides[get_ingestion_service] = lambda: ingestion_service
        app.dependency_overrides[get_active_watchlist_symbols] = lambda: ["AAPL"]
    if repository is not None:
        app.dependency_overrides[get_market_data_repository] = lambda: repository
    if research_service is not None:
        app.dependency_overrides[get_research_assessment_service] = lambda: research_service
    if research_outcome_label_after_assessment_enabled:
        app.state.db_session_factory = lambda: _FakeSessionContext()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


async def test_ingest_returns_run_summary() -> None:
    run_result = IngestionRunResult(
        results=[
            SymbolIngestionResult(
                symbol="AAPL",
                stored_count=1,
                skipped_existing_count=0,
                corrected_count=0,
                rejected_count=1,
                rejections={RejectionReason.STALE: 1},
                latest_trading_date=date(2024, 1, 2),
            )
        ]
    )
    service = _FakeIngestionService(run_result)
    research = _FakeResearchService()

    async with _client_with_overrides(
        ingestion_service=service, research_service=research
    ) as client:
        response = await client.post("/market-data/ingest")

    assert response.status_code == 200
    body = response.json()
    assert body["results"][0]["symbol"] == "AAPL"
    assert body["results"][0]["stored_count"] == 1
    assert body["results"][0]["rejected_count"] == 1
    assert body["results"][0]["rejections"] == {"stale": 1}
    assert body["results"][0]["error"] is None
    assert body["results"][0]["latest_trading_date"] == "2024-01-02"
    assert service.requested_symbols == ["AAPL"]
    assert research.assess_calls == []


async def test_ingest_runs_research_when_flag_enabled() -> None:
    run_result = IngestionRunResult(
        results=[
            SymbolIngestionResult(
                symbol="AAPL",
                stored_count=1,
                skipped_existing_count=0,
                corrected_count=0,
                rejected_count=0,
            )
        ]
    )
    service = _FakeIngestionService(run_result)
    research = _FakeResearchService()

    async with _client_with_overrides(
        ingestion_service=service,
        research_service=research,
        research_schedule_after_ingest_enabled=True,
    ) as client:
        response = await client.post("/market-data/ingest")

    assert response.status_code == 200
    assert research.assess_calls == ["AAPL"]


async def test_ingest_runs_outcome_labels_when_both_flags_enabled() -> None:
    run_result = IngestionRunResult(
        results=[
            SymbolIngestionResult(
                symbol="AAPL",
                stored_count=1,
                skipped_existing_count=0,
                corrected_count=0,
                rejected_count=0,
            )
        ]
    )
    service = _FakeIngestionService(run_result)
    research = _FakeResearchService()

    with patch(
        "aegis.api.routers.market_data.build_outcome_label_service",
        return_value=object(),
    ), patch(
        "aegis.api.routers.market_data.run_outcome_labels_after_research",
        new_callable=AsyncMock,
    ) as mock_labels:
        async with _client_with_overrides(
            ingestion_service=service,
            research_service=research,
            research_schedule_after_ingest_enabled=True,
            research_outcome_label_after_assessment_enabled=True,
        ) as client:
            response = await client.post("/market-data/ingest")

        assert response.status_code == 200
        assert research.assess_calls == ["AAPL"]
        mock_labels.assert_awaited_once()


async def test_get_daily_bars_returns_stored_bars() -> None:
    repository = _FakeRepository([_bar()])

    async with _client_with_overrides(repository=repository) as client:
        response = await client.get("/market-data/AAPL/daily-bars")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["symbol"] == "AAPL"
    assert Decimal(str(body[0]["open"])) == Decimal("100")
    assert body[0]["volume"] == 1000


async def test_get_daily_bars_returns_404_for_unknown_symbol() -> None:
    repository = _FakeRepository([])

    async with _client_with_overrides(repository=repository) as client:
        response = await client.get("/market-data/UNKNOWN/daily-bars")

    assert response.status_code == 404


async def test_get_daily_bars_respects_limit_query_param() -> None:
    repository = _FakeRepository([_bar(), _bar(), _bar()])

    async with _client_with_overrides(repository=repository) as client:
        response = await client.get("/market-data/AAPL/daily-bars", params={"limit": 2})

    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_market_data_returns_401_without_auth_override() -> None:
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

    repository = _FakeRepository([_bar()])
    app = create_app(settings=Settings(environment="test", ingestion_schedule_enabled=False))
    app.dependency_overrides[get_market_data_repository] = lambda: repository
    app.dependency_overrides[get_operator_repository] = lambda: _EmptyOperators()
    app.dependency_overrides[get_session_store] = lambda: _EmptySessions()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/market-data/AAPL/daily-bars")

    assert response.status_code == 401
