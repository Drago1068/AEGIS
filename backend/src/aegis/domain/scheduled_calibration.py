"""Post-assessment probability calibration orchestration (Phase 15).

Framework-free per the domain module boundary: after a successful assessment (and optionally
after labeling), attempt Phase 15 ``research_calibration_v1`` using stored labeled history.
Per-assessment fail-closed skips log and persist nothing. See ADR-0016.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

from aegis.domain.research_assessment import ResearchAssessmentSnapshotData
from aegis.domain.research_probability_calibration import CalibrationUnavailableError
from aegis.domain.scheduled_outcome_labels import OutcomeLabelAfterAssessmentSummary

logger = logging.getLogger(__name__)


class ProbabilityCalibrator(Protocol):
    async def calibrate_assessment(self, symbol: str, assessment_snapshot_id: int) -> object:
        ...


@dataclass(frozen=True, slots=True)
class CalibrationAfterAssessmentOutcome:
    symbol: str
    assessment_snapshot_id: int
    persisted: bool
    reason: str | None = None
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class CalibrationAfterAssessmentSummary:
    outcomes: tuple[CalibrationAfterAssessmentOutcome, ...] = ()

    @property
    def persisted_count(self) -> int:
        return sum(1 for outcome in self.outcomes if outcome.persisted)

    @property
    def skipped_count(self) -> int:
        return sum(1 for outcome in self.outcomes if not outcome.persisted)


async def run_calibrations_after_assessments(
    assessments: list[tuple[str, int]],
    service: ProbabilityCalibrator,
) -> CalibrationAfterAssessmentSummary:
    outcomes: list[CalibrationAfterAssessmentOutcome] = []
    for symbol, assessment_snapshot_id in assessments:
        normalized = symbol.upper()
        try:
            await service.calibrate_assessment(normalized, assessment_snapshot_id)
        except CalibrationUnavailableError as exc:
            logger.info(
                "research_calibration_after_assessment_skipped",
                extra={
                    "symbol": normalized,
                    "assessment_snapshot_id": assessment_snapshot_id,
                    "reason": exc.reason.value,
                    "detail": exc.detail,
                },
            )
            outcomes.append(
                CalibrationAfterAssessmentOutcome(
                    symbol=normalized,
                    assessment_snapshot_id=assessment_snapshot_id,
                    persisted=False,
                    reason=exc.reason.value,
                    detail=exc.detail,
                )
            )
            continue
        except Exception:  # noqa: BLE001 - per-assessment fail-closed; do not abort batch.
            logger.exception(
                "research_calibration_after_assessment_error",
                extra={
                    "symbol": normalized,
                    "assessment_snapshot_id": assessment_snapshot_id,
                },
            )
            outcomes.append(
                CalibrationAfterAssessmentOutcome(
                    symbol=normalized,
                    assessment_snapshot_id=assessment_snapshot_id,
                    persisted=False,
                    reason="unexpected_error",
                    detail="calibration raised unexpectedly",
                )
            )
            continue

        outcomes.append(
            CalibrationAfterAssessmentOutcome(
                symbol=normalized,
                assessment_snapshot_id=assessment_snapshot_id,
                persisted=True,
            )
        )

    summary = CalibrationAfterAssessmentSummary(outcomes=tuple(outcomes))
    logger.info(
        "research_calibration_after_assessment_completed",
        extra={
            "assessment_count": len(assessments),
            "persisted_count": summary.persisted_count,
            "skipped_count": summary.skipped_count,
        },
    )
    return summary


async def run_calibrations_after_labels(
    label_summary: OutcomeLabelAfterAssessmentSummary,
    service: ProbabilityCalibrator,
) -> CalibrationAfterAssessmentSummary:
    assessments = [
        (outcome.symbol, outcome.assessment_snapshot_id)
        for outcome in label_summary.outcomes
        if outcome.persisted
    ]
    return await run_calibrations_after_assessments(assessments, service)


async def try_calibrate_assessment_after_create(
    snapshot: ResearchAssessmentSnapshotData,
    service: ProbabilityCalibrator,
) -> None:
    if snapshot.id is None:
        logger.info(
            "research_calibration_after_assessment_skipped",
            extra={
                "symbol": snapshot.symbol.upper(),
                "reason": "missing_assessment_id",
                "detail": "assessment snapshot id is required to attach calibration",
            },
        )
        return

    try:
        await service.calibrate_assessment(snapshot.symbol, snapshot.id)
    except CalibrationUnavailableError as exc:
        logger.info(
            "research_calibration_after_assessment_skipped",
            extra={
                "symbol": snapshot.symbol.upper(),
                "assessment_snapshot_id": snapshot.id,
                "reason": exc.reason.value,
                "detail": exc.detail,
            },
        )
    except Exception:  # noqa: BLE001 - fail-closed; assessment response already succeeded.
        logger.exception(
            "research_calibration_after_assessment_error",
            extra={
                "symbol": snapshot.symbol.upper(),
                "assessment_snapshot_id": snapshot.id,
            },
        )
