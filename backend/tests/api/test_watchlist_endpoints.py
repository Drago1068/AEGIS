"""Unit tests for the watchlist management endpoints, via dependency overrides.

No real database access: the endpoints are exercised entirely through a fake repository
double substituted with ``app.dependency_overrides``.
"""

from __future__ import annotations

from datetime import UTC, datetime

from httpx import ASGITransport, AsyncClient

from aegis.api.dependencies import get_watchlist_repository
from aegis.api.main import create_app
from aegis.config.settings import Settings
from aegis.persistence.models import WatchlistSymbol


def _row(symbol: str = "AAPL", *, is_active: bool = True) -> WatchlistSymbol:
    return WatchlistSymbol(
        id=1,
        symbol=symbol,
        is_active=is_active,
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
        updated_at=datetime(2024, 1, 1, tzinfo=UTC),
    )


class _FakeWatchlistRepository:
    def __init__(self, rows: list[WatchlistSymbol] | None = None) -> None:
        self._rows: dict[str, WatchlistSymbol] = {row.symbol: row for row in (rows or [])}
        self.added_symbols: list[str] = []
        self.deactivated_symbols: list[str] = []

    async def list_active_rows(self) -> list[WatchlistSymbol]:
        return [row for row in self._rows.values() if row.is_active]

    async def add(self, symbol: str) -> WatchlistSymbol:
        self.added_symbols.append(symbol)
        row = self._rows.get(symbol)
        if row is not None:
            row.is_active = True
            return row
        row = _row(symbol)
        self._rows[symbol] = row
        return row

    async def deactivate(self, symbol: str) -> bool:
        self.deactivated_symbols.append(symbol)
        row = self._rows.get(symbol)
        if row is None or not row.is_active:
            return False
        row.is_active = False
        return True


def _client_with_repository(repository: _FakeWatchlistRepository) -> AsyncClient:
    app = create_app(settings=Settings(environment="test"))
    app.dependency_overrides[get_watchlist_repository] = lambda: repository
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


async def test_list_watchlist_returns_active_symbols_only() -> None:
    repository = _FakeWatchlistRepository([_row("AAPL"), _row("MSFT", is_active=False)])

    async with _client_with_repository(repository) as client:
        response = await client.get("/watchlist")

    assert response.status_code == 200
    body = response.json()
    assert [entry["symbol"] for entry in body] == ["AAPL"]
    assert body[0]["is_active"] is True


async def test_add_watchlist_symbol_normalizes_and_returns_201() -> None:
    repository = _FakeWatchlistRepository()

    async with _client_with_repository(repository) as client:
        response = await client.post("/watchlist", json={"symbol": "  aapl "})

    assert response.status_code == 201
    assert response.json()["symbol"] == "AAPL"
    assert repository.added_symbols == ["AAPL"]


async def test_add_watchlist_symbol_rejects_invalid_shape_with_422() -> None:
    repository = _FakeWatchlistRepository()

    async with _client_with_repository(repository) as client:
        response = await client.post("/watchlist", json={"symbol": "!!!"})

    assert response.status_code == 422
    assert repository.added_symbols == []


async def test_remove_watchlist_symbol_returns_204_when_found() -> None:
    repository = _FakeWatchlistRepository([_row("AAPL")])

    async with _client_with_repository(repository) as client:
        response = await client.delete("/watchlist/aapl")

    assert response.status_code == 204
    assert repository.deactivated_symbols == ["AAPL"]


async def test_remove_watchlist_symbol_returns_404_when_not_found() -> None:
    repository = _FakeWatchlistRepository()

    async with _client_with_repository(repository) as client:
        response = await client.delete("/watchlist/unknown")

    assert response.status_code == 404
