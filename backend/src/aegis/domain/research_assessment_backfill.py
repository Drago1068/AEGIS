"""Historical research assessment backfill (Phase 45/47, ADR-0046 / ADR-0048).

Framework-free batch: pick label-ready candidate as-of dates from stored primary bars,
truncate each series point-in-time, reuse ``assess_from_bars``, append on success, skip
fail-closed without aborting the batch. Does not invent probability_confidence or run
labeling.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import date

from aegis.domain.research_assessment import (
    PRIMARY_QUALITY,
    ResearchAssessmentSnapshotData,
    ResearchAssessmentUnavailableError,
    ResearchBarInput,
    ResearchMultiSourceCoverageConfig,
    assess_from_bars,
)
from aegis.domain.research_outcome_labels import (
    FORWARD_HORIZON_SESSIONS,
    has_stored_forward_horizon_close,
)

logger = logging.getLogger(__name__)

REASON_ALREADY_EXISTS = "assessment_already_exists"
REASON_UNEXPECTED = "unexpected_error"
DEFAULT_MIN_FORWARD_SESSIONS = max(FORWARD_HORIZON_SESSIONS)

SnapshotInserter = Callable[
    [ResearchAssessmentSnapshotData],
    Awaitable[ResearchAssessmentSnapshotData],
]


@dataclass(frozen=True, slots=True)
class AssessmentBackfillOutcome:
    """Outcome for one candidate as-of date in an assessment backfill pass."""

    symbol: str
    as_of_trading_date: date
    persisted: bool
    assessment_snapshot_id: int | None = None
    reason: str | None = None
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class AssessmentBackfillSummary:
    """Aggregate outcomes for one assessment backfill pass."""

    outcomes: tuple[AssessmentBackfillOutcome, ...] = ()

    @property
    def candidate_count(self) -> int:
        return len(self.outcomes)

    @property
    def persisted_count(self) -> int:
        return sum(1 for outcome in self.outcomes if outcome.persisted)

    @property
    def skipped_count(self) -> int:
        return sum(1 for outcome in self.outcomes if not outcome.persisted)


def bars_as_of(
    bars_newest_first: list[ResearchBarInput],
    as_of: date,
) -> list[ResearchBarInput]:
    """Return bars with ``trading_date <= as_of``, preserving newest-first order."""

    return [bar for bar in bars_newest_first if bar.trading_date <= as_of]


def candidate_as_of_dates(
    bars_newest_first: list[ResearchBarInput],
    limit: int,
    *,
    calendar_name: str,
    min_forward_sessions: int = DEFAULT_MIN_FORWARD_SESSIONS,
) -> list[date]:
    """Primary dates newest-first that have stored closes through the label horizon.

    Phase 47 (ADR-0048): omit tip dates without a close on the trading session
    ``min_forward_sessions`` after ``as_of`` so Phase 13 labeling can persist.
    """

    primary_close_dates = {
        bar.trading_date
        for bar in bars_newest_first
        if bar.data_quality == PRIMARY_QUALITY and bar.close > 0
    }
    seen: set[date] = set()
    dates: list[date] = []
    for bar in bars_newest_first:
        if bar.data_quality != PRIMARY_QUALITY:
            continue
        if bar.trading_date in seen:
            continue
        seen.add(bar.trading_date)
        if not has_stored_forward_horizon_close(
            bar.trading_date,
            primary_close_dates,
            calendar_name=calendar_name,
            min_forward_sessions=min_forward_sessions,
        ):
            continue
        dates.append(bar.trading_date)
        if len(dates) >= limit:
            break
    return dates


async def run_assessment_backfill(
    symbol: str,
    *,
    bars_newest_first: list[ResearchBarInput],
    existing_as_of_dates: set[date],
    limit: int,
    calendar_name: str,
    max_latest_bar_staleness_trading_days: int,
    insert_snapshot: SnapshotInserter,
    multi_source: ResearchMultiSourceCoverageConfig | None = None,
    min_forward_sessions: int = DEFAULT_MIN_FORWARD_SESSIONS,
) -> AssessmentBackfillSummary:
    """Assess up to ``limit`` label-ready as-of dates; never abort the batch on one failure.

    ``insert_snapshot`` persists a successful snapshot (typically the assessment store
    insert). Mutates ``existing_as_of_dates`` as rows are persisted so later candidates in
    the same pass are skipped when dates collide.
    """

    normalized = symbol.upper()
    candidates = candidate_as_of_dates(
        bars_newest_first,
        limit,
        calendar_name=calendar_name,
        min_forward_sessions=min_forward_sessions,
    )
    outcomes: list[AssessmentBackfillOutcome] = []

    for as_of in candidates:
        if as_of in existing_as_of_dates:
            outcomes.append(
                AssessmentBackfillOutcome(
                    symbol=normalized,
                    as_of_trading_date=as_of,
                    persisted=False,
                    reason=REASON_ALREADY_EXISTS,
                    detail=f"assessment already exists for as_of {as_of.isoformat()}",
                )
            )
            continue

        truncated = bars_as_of(bars_newest_first, as_of)
        try:
            snapshot = assess_from_bars(
                normalized,
                truncated,
                calendar_name=calendar_name,
                max_latest_bar_staleness_trading_days=max_latest_bar_staleness_trading_days,
                as_of=as_of,
                multi_source=multi_source,
            )
            persisted = await insert_snapshot(snapshot)
        except ResearchAssessmentUnavailableError as exc:
            logger.info(
                "research_assessment_backfill_skipped",
                extra={
                    "symbol": normalized,
                    "as_of_trading_date": as_of.isoformat(),
                    "reason": exc.reason.value,
                    "detail": exc.detail,
                },
            )
            outcomes.append(
                AssessmentBackfillOutcome(
                    symbol=normalized,
                    as_of_trading_date=as_of,
                    persisted=False,
                    reason=exc.reason.value,
                    detail=exc.detail,
                )
            )
            continue
        except Exception:  # noqa: BLE001 - per-date fail-closed; do not abort the batch.
            logger.exception(
                "research_assessment_backfill_error",
                extra={
                    "symbol": normalized,
                    "as_of_trading_date": as_of.isoformat(),
                },
            )
            outcomes.append(
                AssessmentBackfillOutcome(
                    symbol=normalized,
                    as_of_trading_date=as_of,
                    persisted=False,
                    reason=REASON_UNEXPECTED,
                    detail="assessment backfill raised unexpectedly",
                )
            )
            continue

        existing_as_of_dates.add(persisted.as_of_trading_date)
        outcomes.append(
            AssessmentBackfillOutcome(
                symbol=normalized,
                as_of_trading_date=persisted.as_of_trading_date,
                persisted=True,
                assessment_snapshot_id=persisted.id,
            )
        )

    summary = AssessmentBackfillSummary(outcomes=tuple(outcomes))
    logger.info(
        "research_assessment_backfill_completed",
        extra={
            "symbol": normalized,
            "candidate_count": summary.candidate_count,
            "persisted_count": summary.persisted_count,
            "skipped_count": summary.skipped_count,
        },
    )
    return summary
