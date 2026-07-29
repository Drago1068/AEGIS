"""Post-assessment outcome label orchestration (Phase 14).

Framework-free per the domain module boundary in ``docs/architecture/overview.md``: after a
successful research assessment, attempt Phase 13 ``forward_total_return_v1`` labeling using stored
bars only. Per-assessment fail-closed: persist an append-only label row on success; on gate
failure or unexpected error, log and skip with no row. See
``docs/architecture/decisions/0015-phase-14-scheduled-outcome-labels.md``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

from aegis.domain.research_assessment import ResearchAssessmentSnapshotData
from aegis.domain.research_outcome_labels import OutcomeLabelUnavailableError
from aegis.domain.scheduled_research import ResearchAfterIngestSummary

logger = logging.getLogger(__name__)


class OutcomeLabeler(Protocol):
    """The minimal label boundary required after assessment (satisfied by
    ``OutcomeLabelService``)."""

    async def label_assessment(self, symbol: str, assessment_snapshot_id: int) -> object:
        """Compute and persist outcome labels, or raise fail-closed."""
        ...


@dataclass(frozen=True, slots=True)
class OutcomeLabelAfterAssessmentOutcome:
    """Outcome for one assessment in a post-assessment labeling pass."""

    symbol: str
    assessment_snapshot_id: int
    persisted: bool
    reason: str | None = None
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class OutcomeLabelAfterAssessmentSummary:
    """Aggregate outcomes for one post-assessment labeling pass."""

    outcomes: tuple[OutcomeLabelAfterAssessmentOutcome, ...] = ()

    @property
    def persisted_count(self) -> int:
        return sum(1 for outcome in self.outcomes if outcome.persisted)

    @property
    def skipped_count(self) -> int:
        return sum(1 for outcome in self.outcomes if not outcome.persisted)


async def run_outcome_labels_after_assessments(
    assessments: list[tuple[str, int]],
    service: OutcomeLabeler,
) -> OutcomeLabelAfterAssessmentSummary:
    """Label each ``(symbol, assessment_snapshot_id)``; never abort the batch on one failure.

    Reuses Phase 13 ``OutcomeLabelService.label_assessment`` (or any ``OutcomeLabeler``). Does
    not call market-data providers. Unexpected exceptions are treated as fail-closed skips.
    """

    outcomes: list[OutcomeLabelAfterAssessmentOutcome] = []
    for symbol, assessment_snapshot_id in assessments:
        normalized = symbol.upper()
        try:
            await service.label_assessment(normalized, assessment_snapshot_id)
        except OutcomeLabelUnavailableError as exc:
            logger.info(
                "outcome_label_after_assessment_skipped",
                extra={
                    "symbol": normalized,
                    "assessment_snapshot_id": assessment_snapshot_id,
                    "reason": exc.reason.value,
                    "detail": exc.detail,
                },
            )
            outcomes.append(
                OutcomeLabelAfterAssessmentOutcome(
                    symbol=normalized,
                    assessment_snapshot_id=assessment_snapshot_id,
                    persisted=False,
                    reason=exc.reason.value,
                    detail=exc.detail,
                )
            )
            continue
        except Exception:  # noqa: BLE001 - per-assessment fail-closed; do not abort the batch.
            logger.exception(
                "outcome_label_after_assessment_error",
                extra={
                    "symbol": normalized,
                    "assessment_snapshot_id": assessment_snapshot_id,
                },
            )
            outcomes.append(
                OutcomeLabelAfterAssessmentOutcome(
                    symbol=normalized,
                    assessment_snapshot_id=assessment_snapshot_id,
                    persisted=False,
                    reason="unexpected_error",
                    detail="labeling raised unexpectedly",
                )
            )
            continue

        outcomes.append(
            OutcomeLabelAfterAssessmentOutcome(
                symbol=normalized,
                assessment_snapshot_id=assessment_snapshot_id,
                persisted=True,
            )
        )

    summary = OutcomeLabelAfterAssessmentSummary(outcomes=tuple(outcomes))
    logger.info(
        "outcome_label_after_assessment_completed",
        extra={
            "assessment_count": len(assessments),
            "persisted_count": summary.persisted_count,
            "skipped_count": summary.skipped_count,
        },
    )
    return summary


async def run_outcome_labels_after_research(
    research_summary: ResearchAfterIngestSummary,
    service: OutcomeLabeler,
) -> OutcomeLabelAfterAssessmentSummary:
    """Label assessments that succeeded in a post-ingest research pass."""

    assessments = [
        (outcome.symbol, outcome.assessment_snapshot_id)
        for outcome in research_summary.outcomes
        if outcome.persisted and outcome.assessment_snapshot_id is not None
    ]
    return await run_outcome_labels_after_assessments(assessments, service)


async def try_label_assessment_after_create(
    snapshot: ResearchAssessmentSnapshotData,
    service: OutcomeLabeler,
) -> None:
    """Attempt labeling for one on-demand assessment; never raise to callers."""

    if snapshot.id is None:
        logger.info(
            "outcome_label_after_assessment_skipped",
            extra={
                "symbol": snapshot.symbol.upper(),
                "reason": "missing_assessment_id",
                "detail": "assessment snapshot id is required to attach outcome labels",
            },
        )
        return

    try:
        await service.label_assessment(snapshot.symbol, snapshot.id)
    except OutcomeLabelUnavailableError as exc:
        logger.info(
            "outcome_label_after_assessment_skipped",
            extra={
                "symbol": snapshot.symbol.upper(),
                "assessment_snapshot_id": snapshot.id,
                "reason": exc.reason.value,
                "detail": exc.detail,
            },
        )
    except Exception:  # noqa: BLE001 - fail-closed; assessment response already succeeded.
        logger.exception(
            "outcome_label_after_assessment_error",
            extra={
                "symbol": snapshot.symbol.upper(),
                "assessment_snapshot_id": snapshot.id,
            },
        )
