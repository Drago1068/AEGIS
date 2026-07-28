"""On-demand market data ingestion and read endpoints.

Protected by operator session auth (Phase 4, ADR-0005). No scoring, recommendation,
prediction, or trading logic is computed here or anywhere in this router. In-process
scheduled ingestion does not use HTTP auth (same process; see ADR-0005).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from aegis.api.dependencies import (
    get_active_watchlist_symbols,
    get_ingestion_service,
    get_market_data_repository,
    require_operator,
)
from aegis.api.schemas.market_data import (
    DailyBarResponse,
    IngestionRunResponse,
    IngestionSymbolResult,
)
from aegis.domain.market_data_ingestion import MarketDataIngestionService
from aegis.persistence.repositories.market_data import MarketDailyBarRepository

router = APIRouter(
    prefix="/market-data",
    tags=["market-data"],
    dependencies=[Depends(require_operator)],
)


@router.post("/ingest", response_model=IngestionRunResponse)
async def ingest_market_data(
    service: MarketDataIngestionService = Depends(get_ingestion_service),
    symbols: list[str] = Depends(get_active_watchlist_symbols),
) -> IngestionRunResponse:
    """Run one ingestion cycle over the current active database-backed watchlist."""

    run_result = await service.run(symbols)
    return IngestionRunResponse(
        results=[
            IngestionSymbolResult.model_validate(result) for result in run_result.results
        ]
    )


@router.get("/{symbol}/daily-bars", response_model=list[DailyBarResponse])
async def get_daily_bars(
    symbol: str,
    limit: int = Query(default=100, ge=1, le=500),
    repository: MarketDailyBarRepository = Depends(get_market_data_repository),
) -> list[DailyBarResponse]:
    """Return up to ``limit`` most recent stored daily bars for ``symbol``, newest first."""

    bars = await repository.list_recent(symbol.upper(), limit)
    if not bars:
        raise HTTPException(
            status_code=404, detail=f"no stored daily bars for symbol {symbol!r}"
        )
    return [DailyBarResponse.model_validate(bar) for bar in bars]
