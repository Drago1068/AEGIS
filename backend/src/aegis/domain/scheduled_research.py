"""Post-ingest research assessment orchestration (Phase 8).

Framework-free per the domain module boundary in ``docs/architecture/overview.md``: after a
successful ingestion cycle, run Phase 6 method ``daily_bar_research_v1`` for each active
watchlist symbol using **stored bars only** (no provider calls). Per-symbol fail-closed:
persist an append-only snapshot on success; on gate failure or unexpected error, log and
skip with no row. See ``docs/architecture/decisions/0009-phase-8-scheduled-research.md``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

from aegis.domain.research_assessment import (
    ResearchAssessmentSnapshotData,
    ResearchAssessmentUnavailableError,
)

logger = logging.getLogger(__name__)


class ResearchAssessor(Protocol):
    """The minimal assess boundary required after ingest (satisfied by
    ``ResearchAssessmentService``)."""

    async def assess(self, symbol: str) -> ResearchAssessmentSnapshotData:
        """Compute and persist one research-only assessment, or raise fail-closed."""
        ...


@dataclass(frozen=True, slots=True)
class ResearchAfterIngestSymbolOutcome:
    """Outcome for one symbol in a post-ingest research pass."""

    symbol: str
    persisted: bool
    reason: str | None = None
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class ResearchAfterIngestSummary:
    """Aggregate outcomes for one post-ingest research pass over the watchlist."""

    outcomes: tuple[ResearchAfterIngestSymbolOutcome, ...] = ()

    @property
    def persisted_count(self) -> int:
        return sum(1 for outcome in self.outcomes if outcome.persisted)

    @property
    def skipped_count(self) -> int:
        return sum(1 for outcome in self.outcomes if not outcome.persisted)


async def run_research_after_ingest(
    symbols: list[str],
    service: ResearchAssessor,
) -> ResearchAfterIngestSummary:
    """Assess each symbol via ``service``; never abort the batch on a single failure.

    Reuses Phase 6 ``ResearchAssessmentService.assess`` (or any ``ResearchAssessor``). Does
    not call market-data providers. Unexpected exceptions are treated as fail-closed skips
    so a locked ingestion cycle can still release its lock cleanly.
    """

    outcomes: list[ResearchAfterIngestSymbolOutcome] = []
    for symbol in symbols:
        normalized = symbol.upper()
        try:
            await service.assess(normalized)
        except ResearchAssessmentUnavailableError as exc:
            logger.info(
                "research_after_ingest_skipped",
                extra={
                    "symbol": normalized,
                    "reason": exc.reason.value,
                    "detail": exc.detail,
                },
            )
            outcomes.append(
                ResearchAfterIngestSymbolOutcome(
                    symbol=normalized,
                    persisted=False,
                    reason=exc.reason.value,
                    detail=exc.detail,
                )
            )
            continue
        except Exception:  # noqa: BLE001 - per-symbol fail-closed; do not abort the batch.
            logger.exception(
                "research_after_ingest_error",
                extra={"symbol": normalized},
            )
            outcomes.append(
                ResearchAfterIngestSymbolOutcome(
                    symbol=normalized,
                    persisted=False,
                    reason="unexpected_error",
                    detail="assessment raised unexpectedly",
                )
            )
            continue

        outcomes.append(ResearchAfterIngestSymbolOutcome(symbol=normalized, persisted=True))

    summary = ResearchAfterIngestSummary(outcomes=tuple(outcomes))
    logger.info(
        "research_after_ingest_completed",
        extra={
            "symbol_count": len(symbols),
            "persisted_count": summary.persisted_count,
            "skipped_count": summary.skipped_count,
        },
    )
    return summary
