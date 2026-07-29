"""On-demand market data ingestion and read endpoints.

Protected by operator session auth (Phase 4, ADR-0005). No scoring, recommendation,
prediction, or trading logic is computed here or anywhere in this router. In-process
scheduled ingestion does not use HTTP auth (same process; see ADR-0005).

When ``AEGIS_RESEARCH_SCHEDULE_AFTER_INGEST_ENABLED`` is true, a successful ingest also
runs Phase 6 research assessments over stored bars for the same watchlist (ADR-0009).
When ``AEGIS_RESEARCH_OUTCOME_LABEL_AFTER_ASSESSMENT_ENABLED`` is true, successful
assessments from that path also attempt Phase 13 outcome labels (ADR-0015).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from aegis.api.dependencies import (
    build_outcome_label_service,
    get_active_watchlist_symbols,
    get_ingestion_service,
    get_market_data_repository,
    get_research_assessment_service,
    require_operator,
)
from aegis.api.schemas.market_data import (
    DailyBarResponse,
    IngestionRunResponse,
    IngestionSymbolResult,
)
from aegis.domain.market_data_ingestion import MarketDataIngestionService
from aegis.domain.research_assessment import ResearchAssessmentService
from aegis.domain.scheduled_outcome_labels import run_outcome_labels_after_research
from aegis.domain.scheduled_research import run_research_after_ingest
from aegis.persistence.repositories.market_data import MarketDailyBarRepository
from aegis.persistence.repositories.research_assessment import ResearchAssessmentRepository
from aegis.persistence.repositories.research_outcome_labels import ResearchOutcomeLabelRepository

router = APIRouter(
    prefix="/market-data",
    tags=["market-data"],
    dependencies=[Depends(require_operator)],
)


@router.post("/ingest", response_model=IngestionRunResponse)
async def ingest_market_data(
    request: Request,
    service: MarketDataIngestionService = Depends(get_ingestion_service),
    symbols: list[str] = Depends(get_active_watchlist_symbols),
    research_service: ResearchAssessmentService = Depends(get_research_assessment_service),
) -> IngestionRunResponse:
    """Run one ingestion cycle over the current active database-backed watchlist.

    When post-ingest research is enabled, assessments run after ingest completes using
    stored bars only (no extra provider calls). Fail-closed skips do not fail this response.
    """

    run_result = await service.run(symbols)
    settings = request.app.state.settings
    if settings.research_schedule_after_ingest_enabled:
        research_summary = await run_research_after_ingest(symbols, research_service)
        if settings.research_outcome_label_after_assessment_enabled:
            async with request.app.state.db_session_factory() as session:
                market_data_repository = MarketDailyBarRepository(session)
                assessment_repository = ResearchAssessmentRepository(session)
                outcome_label_service = build_outcome_label_service(
                    market_data_repository,
                    assessment_repository,
                    ResearchOutcomeLabelRepository(session),
                    settings,
                )
                await run_outcome_labels_after_research(research_summary, outcome_label_service)
    return IngestionRunResponse(
        results=[IngestionSymbolResult.model_validate(result) for result in run_result.results]
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
        raise HTTPException(status_code=404, detail=f"no stored daily bars for symbol {symbol!r}")
    return [DailyBarResponse.model_validate(bar) for bar in bars]
