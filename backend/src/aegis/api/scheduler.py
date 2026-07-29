"""Wiring between FastAPI application state and the scheduled ingestion domain logic.

Kept in ``api/`` (not ``domain/``) because it depends on concrete infrastructure - APScheduler,
the real Redis client, and a live database session - which ``domain/`` must not import
directly (see the module boundary in ``docs/architecture/overview.md``). The actual
lock-and-run decision logic lives in ``aegis.domain.scheduled_ingestion``, which is
framework-free and independently unit tested; this module only wires real objects into it,
mirroring ``aegis.api.dependencies``. See
``docs/architecture/decisions/0003-phase-2-scheduled-watchlist.md`` and
``docs/architecture/decisions/0009-phase-8-scheduled-research.md`` and
``docs/architecture/decisions/0015-phase-14-scheduled-outcome-labels.md``.
"""

from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import (  # pyright: ignore[reportMissingTypeStubs]
    AsyncIOScheduler,
)
from apscheduler.triggers.cron import CronTrigger  # pyright: ignore[reportMissingTypeStubs]
from fastapi import FastAPI

from aegis.api.dependencies import (
    build_outcome_label_service,
    build_research_assessment_service,
    build_research_calibration_service,
)
from aegis.api.ingestion_wiring import build_market_data_ingestion_service
from aegis.config.settings import Settings
from aegis.domain.scheduled_ingestion import run_locked_ingestion_cycle
from aegis.persistence.repositories.market_data import MarketDailyBarRepository
from aegis.persistence.repositories.research_assessment import ResearchAssessmentRepository
from aegis.persistence.repositories.research_outcome_labels import ResearchOutcomeLabelRepository
from aegis.persistence.repositories.research_probability_calibration import (
    ResearchProbabilityCalibrationRepository,
)
from aegis.persistence.repositories.watchlist import WatchlistRepository

logger = logging.getLogger(__name__)

_JOB_ID = "scheduled_market_data_ingestion"


async def run_scheduled_ingestion_job(app: FastAPI) -> None:
    """Run one locked ingestion cycle using the real objects wired onto ``app.state``."""

    settings: Settings = app.state.settings
    async with app.state.db_session_factory() as session:
        watchlist_repository = WatchlistRepository(session)
        market_data_repository = MarketDailyBarRepository(session)
        ingestion_service = build_market_data_ingestion_service(
            settings, app.state.http_client, market_data_repository
        )
        research_service = None
        outcome_label_service = None
        calibration_service = None
        calibration_repository = ResearchProbabilityCalibrationRepository(session)
        assessment_repository = ResearchAssessmentRepository(session)
        if settings.research_schedule_after_ingest_enabled:
            research_service = build_research_assessment_service(
                market_data_repository,
                assessment_repository,
                settings,
            )
        if (
            settings.research_outcome_label_after_assessment_enabled
            and research_service is not None
        ):
            outcome_label_service = build_outcome_label_service(
                market_data_repository,
                assessment_repository,
                ResearchOutcomeLabelRepository(session),
                settings,
            )
        if (
            settings.research_calibration_after_label_enabled
            and research_service is not None
        ):
            calibration_service = build_research_calibration_service(
                assessment_repository,
                calibration_repository,
                settings,
            )
        await run_locked_ingestion_cycle(
            redis_client=app.state.redis_client,
            lock_key=settings.ingestion_schedule_lock_key,
            lock_ttl_seconds=settings.ingestion_schedule_lock_ttl_seconds,
            watchlist=watchlist_repository,
            seed_symbols=settings.watchlist_seed_symbols,
            ingestion_service=ingestion_service,
            research_service=research_service,
            outcome_label_service=outcome_label_service,
            calibration_service=calibration_service,
        )


class IngestionScheduler:
    """Thin wrapper around an APScheduler ``AsyncIOScheduler`` running the ingestion job.

    APScheduler ships no type stubs (no ``py.typed`` marker), so its public surface is
    ``Any``/``Unknown`` to pyright; the ignore comments below make every crossing point
    explicit rather than letting ``Unknown`` silently propagate.
    """

    def __init__(self, app: FastAPI, cron_expression: str) -> None:
        self._app = app
        self._cron_expression = cron_expression
        self._scheduler = AsyncIOScheduler(timezone="UTC")  # pyright: ignore[reportUnknownMemberType]

    async def _run_job(self) -> None:
        await run_scheduled_ingestion_job(self._app)

    def start(self) -> None:
        """Register the cron-triggered ingestion job and start the scheduler."""

        trigger = CronTrigger.from_crontab(  # pyright: ignore[reportUnknownMemberType]
            self._cron_expression, timezone="UTC"
        )
        self._scheduler.add_job(  # pyright: ignore[reportUnknownMemberType]
            self._run_job, trigger, id=_JOB_ID, replace_existing=True
        )
        self._scheduler.start()  # pyright: ignore[reportUnknownMemberType]
        logger.info("ingestion_scheduler_started", extra={"cron": self._cron_expression})

    def shutdown(self) -> None:
        """Stop the scheduler without waiting for any in-flight job to finish."""

        self._scheduler.shutdown(wait=False)  # pyright: ignore[reportUnknownMemberType]
        logger.info("ingestion_scheduler_stopped")
