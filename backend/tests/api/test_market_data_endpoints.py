"""Unit tests for the market data ingest/read endpoints, via dependency overrides.

No real network or database access: both endpoints are exercised entirely through fake
doubles substituted with ``app.dependency_overrides``.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from httpx import ASGITransport, AsyncClient

from aegis.api.dependencies import (
    get_ingestion_service,
    get_market_data_repository,
    get_watchlist_symbols,
)
from aegis.api.main import create_app
from aegis.config.settings import Settings
from aegis.domain.market_data_ingestion import IngestionRunResult, SymbolIngestionResult
from aegis.domain.market_data_validation import RejectionReason
from aegis.persistence.models import MarketDailyBarObservation


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
    )


def _client_with_overrides(
    *,
    ingestion_service: _FakeIngestionService | None = None,
    repository: _FakeRepository | None = None,
) -> AsyncClient:
    app = create_app(settings=Settings(environment="test"))
    if ingestion_service is not None:
        app.dependency_overrides[get_ingestion_service] = lambda: ingestion_service
        app.dependency_overrides[get_watchlist_symbols] = lambda: ["AAPL"]
    if repository is not None:
        app.dependency_overrides[get_market_data_repository] = lambda: repository
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


async def test_ingest_returns_run_summary() -> None:
    run_result = IngestionRunResult(
        results=[
            SymbolIngestionResult(
                symbol="AAPL",
                stored_count=1,
                skipped_existing_count=0,
                rejected_count=1,
                rejections={RejectionReason.STALE: 1},
            )
        ]
    )
    service = _FakeIngestionService(run_result)

    async with _client_with_overrides(ingestion_service=service) as client:
        response = await client.post("/market-data/ingest")

    assert response.status_code == 200
    body = response.json()
    assert body["results"][0]["symbol"] == "AAPL"
    assert body["results"][0]["stored_count"] == 1
    assert body["results"][0]["rejected_count"] == 1
    assert body["results"][0]["rejections"] == {"stale": 1}
    assert body["results"][0]["error"] is None
    assert service.requested_symbols == ["AAPL"]


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
