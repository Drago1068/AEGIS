"""FastAPI dependency providers for readiness checks and request-scoped services.

These are defined as separate, overridable dependencies (rather than being called directly
inside the router) so unit tests can substitute fakes for each dependency independently via
``app.dependency_overrides``, covering both the available and unavailable outcome for each
dependency without a real database or Redis instance.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from aegis.api.ingestion_wiring import build_market_data_ingestion_service
from aegis.config.settings import Settings
from aegis.domain.market_data_ingestion import MarketDataIngestionService
from aegis.domain.research_assessment import (
    ResearchAssessmentService,
    ResearchAssessmentSnapshotData,
    ResearchBarInput,
    ResearchMultiSourceCoverageConfig,
)
from aegis.domain.research_outcome_labels import OutcomeLabelService
from aegis.domain.research_probability_calibration import (
    ResearchProbabilityCalibrationService,
    apply_probability_calibration,
)
from aegis.persistence.cache import check_redis
from aegis.persistence.database import check_database
from aegis.persistence.models import MarketDailyBarObservation, Operator
from aegis.persistence.repositories.market_data import MarketDailyBarRepository
from aegis.persistence.repositories.operators import OperatorRepository
from aegis.persistence.repositories.research_assessment import ResearchAssessmentRepository
from aegis.persistence.repositories.research_outcome_labels import ResearchOutcomeLabelRepository
from aegis.persistence.repositories.research_probability_calibration import (
    ResearchProbabilityCalibrationRepository,
)
from aegis.persistence.repositories.watchlist import WatchlistRepository
from aegis.persistence.sessions import RedisSessionStore, SessionStore


async def check_database_ready(request: Request) -> bool:
    """Readiness dependency for PostgreSQL/TimescaleDB."""

    settings = request.app.state.settings
    engine = request.app.state.db_engine
    return await check_database(engine, settings.readiness_timeout_seconds)


async def check_redis_ready(request: Request) -> bool:
    """Readiness dependency for Redis."""

    settings = request.app.state.settings
    client = request.app.state.redis_client
    return await check_redis(client, settings.readiness_timeout_seconds)


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    """A request-scoped database session, closed when the request finishes."""

    session_factory = request.app.state.db_session_factory
    async with session_factory() as session:
        yield session


async def get_market_data_repository(
    session: AsyncSession = Depends(get_db_session),
) -> MarketDailyBarRepository:
    """A request-scoped repository for stored daily bar observations."""

    return MarketDailyBarRepository(session)


async def get_watchlist_repository(
    session: AsyncSession = Depends(get_db_session),
) -> WatchlistRepository:
    """A request-scoped repository for the database-backed watchlist."""

    return WatchlistRepository(session)


async def get_operator_repository(
    session: AsyncSession = Depends(get_db_session),
) -> OperatorRepository:
    """A request-scoped repository for operator accounts."""

    return OperatorRepository(session)


async def get_session_store(request: Request) -> SessionStore:
    """Redis-backed session store using the process client and configured TTL."""

    settings = request.app.state.settings
    return RedisSessionStore(request.app.state.redis_client, settings.session_ttl_seconds)


async def require_operator(
    request: Request,
    repository: OperatorRepository = Depends(get_operator_repository),
    session_store: SessionStore = Depends(get_session_store),
) -> Operator:
    """Require a valid operator session cookie; return the authenticated operator.

    Seeds the operators table from env credentials when empty (same lazy path as login).
    Fails closed with HTTP 401 when the cookie is missing, the Redis session is gone, or the
    operator row no longer exists. See ADR-0005.
    """

    settings = request.app.state.settings
    await repository.ensure_seeded(settings.operator_username, settings.operator_password)

    session_id = request.cookies.get(settings.session_cookie_name)
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication required",
        )

    session = await session_store.get(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication required",
        )

    operator = await repository.get_by_username(session.username)
    if operator is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication required",
        )
    return operator


async def get_active_watchlist_symbols(
    request: Request,
    repository: WatchlistRepository = Depends(get_watchlist_repository),
) -> list[str]:
    """The current active watchlist, seeding it from ``AEGIS_WATCHLIST_SYMBOLS`` if empty.

    Replaces the Phase 1 environment-only watchlist (ADR-0003): the database is now the
    source of truth, and the environment variable is only a one-time bootstrap seed.
    """

    settings = request.app.state.settings
    await repository.ensure_seeded(settings.watchlist_seed_symbols)
    return await repository.list_active()


async def get_ingestion_service(
    request: Request,
    repository: MarketDailyBarRepository = Depends(get_market_data_repository),
) -> MarketDataIngestionService:
    """A request-scoped ingestion service wired to configured primary/secondary providers."""

    settings = request.app.state.settings
    return build_market_data_ingestion_service(
        settings, request.app.state.http_client, repository
    )


class ResearchBarReaderAdapter:
    """Maps stored daily bar ORM rows to domain :class:`ResearchBarInput` values."""

    def __init__(self, repository: MarketDailyBarRepository) -> None:
        self._repository = repository

    async def list_recent_bars(self, symbol: str, limit: int) -> list[ResearchBarInput]:
        rows = await self._repository.list_recent(symbol, limit)
        return [_bar_to_research_input(row) for row in rows]


def _bar_to_research_input(row: MarketDailyBarObservation) -> ResearchBarInput:
    return ResearchBarInput(
        trading_date=row.trading_date,
        open=row.open,
        high=row.high,
        low=row.low,
        close=row.close,
        volume=row.volume,
        data_quality=row.data_quality,
        source=row.source,
    )


def build_research_assessment_service(
    market_data_repository: MarketDailyBarRepository,
    snapshot_repository: ResearchAssessmentRepository,
    settings: Settings,
) -> ResearchAssessmentService:
    """Wire research assessment domain service for HTTP and scheduler paths."""

    multi_source = ResearchMultiSourceCoverageConfig(
        enabled=settings.research_multi_source_coverage_enabled,
        primary_source=settings.daily_bar_primary_source,
        secondary_source=settings.daily_bar_secondary_source,
        close_tolerance=settings.research_multi_source_close_tolerance,
        disagreement_fail_closed=settings.research_multi_source_disagreement_fail_closed,
        allow_cross_source_component_fill=settings.research_allow_cross_source_component_fill,
    )
    return ResearchAssessmentService(
        ResearchBarReaderAdapter(market_data_repository),
        snapshot_repository,
        calendar_name=settings.exchange_calendar_name,
        max_latest_bar_staleness_trading_days=settings.max_latest_bar_staleness_trading_days,
        multi_source=multi_source,
        bar_load_limit=settings.research_bar_load_limit,
    )


async def get_research_assessment_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ResearchAssessmentRepository:
    """A request-scoped repository for research assessment snapshots."""

    return ResearchAssessmentRepository(session)


async def get_research_assessment_service(
    request: Request,
    market_data_repository: MarketDailyBarRepository = Depends(get_market_data_repository),
    snapshot_repository: ResearchAssessmentRepository = Depends(get_research_assessment_repository),
) -> ResearchAssessmentService:
    """Wire research assessment domain service to bar reader and snapshot store."""

    return build_research_assessment_service(
        market_data_repository,
        snapshot_repository,
        request.app.state.settings,
    )


async def get_outcome_label_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ResearchOutcomeLabelRepository:
    """A request-scoped repository for research outcome labels."""

    return ResearchOutcomeLabelRepository(session)


async def get_outcome_label_service(
    request: Request,
    market_data_repository: MarketDailyBarRepository = Depends(get_market_data_repository),
    assessment_repository: ResearchAssessmentRepository = Depends(
        get_research_assessment_repository
    ),
    label_repository: ResearchOutcomeLabelRepository = Depends(get_outcome_label_repository),
) -> OutcomeLabelService:
    """Wire outcome label service to assessment store, bars, and label persistence."""

    return build_outcome_label_service(
        market_data_repository,
        assessment_repository,
        label_repository,
        request.app.state.settings,
    )


def build_outcome_label_service(
    market_data_repository: MarketDailyBarRepository,
    assessment_repository: ResearchAssessmentRepository,
    label_repository: ResearchOutcomeLabelRepository,
    settings: Settings,
) -> OutcomeLabelService:
    """Wire outcome label domain service for HTTP and scheduler paths."""

    return OutcomeLabelService(
        assessment_repository,
        ResearchBarReaderAdapter(market_data_repository),
        label_repository,
        calendar_name=settings.exchange_calendar_name,
        bar_load_limit=settings.research_bar_load_limit,
    )


async def get_research_calibration_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ResearchProbabilityCalibrationRepository:
    """A request-scoped repository for labeled corpus reads and calibrations."""

    return ResearchProbabilityCalibrationRepository(session)


async def get_research_calibration_service(
    request: Request,
    assessment_repository: ResearchAssessmentRepository = Depends(
        get_research_assessment_repository
    ),
    calibration_repository: ResearchProbabilityCalibrationRepository = Depends(
        get_research_calibration_repository
    ),
) -> ResearchProbabilityCalibrationService:
    """Wire research probability calibration domain service."""

    return build_research_calibration_service(
        assessment_repository,
        calibration_repository,
        request.app.state.settings,
    )


def build_research_calibration_service(
    assessment_repository: ResearchAssessmentRepository,
    calibration_repository: ResearchProbabilityCalibrationRepository,
    settings: Settings,
) -> ResearchProbabilityCalibrationService:
    """Wire calibration service for HTTP and scheduler paths."""

    return ResearchProbabilityCalibrationService(
        assessment_repository,
        calibration_repository,
        calibration_repository,
        min_corpus=settings.research_calibration_min_corpus,
        min_bucket=settings.research_calibration_min_bucket,
        index_bucket_width=settings.research_calibration_index_bucket_width,
    )


async def enrich_assessment_with_calibration(
    snapshot: ResearchAssessmentSnapshotData,
    calibration_repository: ResearchProbabilityCalibrationRepository,
) -> ResearchAssessmentSnapshotData:
    """Overlay the latest append-only calibration row for API responses."""

    if snapshot.id is None:
        return snapshot
    calibration = await calibration_repository.get_latest_for_assessment(snapshot.id)
    return apply_probability_calibration(snapshot, calibration)
