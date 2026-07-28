"""Database-backed watchlist management endpoints (Phase 2, see ADR-0003).

Protected by operator session auth (Phase 4, ADR-0005). No scoring, recommendation,
prediction, or trading logic is computed here or anywhere in this router.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from aegis.api.dependencies import get_watchlist_repository, require_operator
from aegis.api.schemas.watchlist import WatchlistAddRequest, WatchlistSymbolResponse
from aegis.persistence.repositories.watchlist import WatchlistRepository

router = APIRouter(
    prefix="/watchlist",
    tags=["watchlist"],
    dependencies=[Depends(require_operator)],
)


@router.get("", response_model=list[WatchlistSymbolResponse])
async def list_watchlist(
    repository: WatchlistRepository = Depends(get_watchlist_repository),
) -> list[WatchlistSymbolResponse]:
    """Return every active watchlist symbol."""

    rows = await repository.list_active_rows()
    return [WatchlistSymbolResponse.model_validate(row) for row in rows]


@router.post("", response_model=WatchlistSymbolResponse, status_code=status.HTTP_201_CREATED)
async def add_watchlist_symbol(
    body: WatchlistAddRequest,
    repository: WatchlistRepository = Depends(get_watchlist_repository),
) -> WatchlistSymbolResponse:
    """Add a symbol to the watchlist, or reactivate it if it was previously removed."""

    row = await repository.add(body.symbol)
    return WatchlistSymbolResponse.model_validate(row)


@router.delete("/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_watchlist_symbol(
    symbol: str,
    repository: WatchlistRepository = Depends(get_watchlist_repository),
) -> None:
    """Deactivate a symbol so future ingestion runs (on-demand or scheduled) skip it."""

    removed = await repository.deactivate(symbol.strip().upper())
    if not removed:
        raise HTTPException(
            status_code=404, detail=f"symbol {symbol!r} is not on the watchlist"
        )
