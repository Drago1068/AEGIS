"""Outcome-label backfill candidate selection (Phase 49, ADR-0050).

Prefer assessments that lack a default-method label and have stored forward-horizon closes,
so tip / already-labeled rows do not consume the operator ``limit``.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from aegis.domain.research_assessment import ResearchAssessmentSnapshotData, ResearchBarInput
from aegis.domain.research_outcome_labels import has_stored_forward_horizon_close

BACKFILL_SCAN_LIMIT = 100


def label_ready_as_of_dates(
    bars_newest_first: Sequence[ResearchBarInput],
    *,
    calendar_name: str,
    min_forward_sessions: int | None = None,
) -> set[date]:
    """Trading dates in ``bars`` that have a stored close on the forward-horizon end."""

    close_dates = {
        bar.trading_date for bar in bars_newest_first if bar.close > 0
    }
    ready: set[date] = set()
    for trading_date in close_dates:
        if has_stored_forward_horizon_close(
            trading_date,
            close_dates,
            calendar_name=calendar_name,
            min_forward_sessions=min_forward_sessions,
        ):
            ready.add(trading_date)
    return ready


def select_label_backfill_candidates(
    snapshots_newest_first: Sequence[ResearchAssessmentSnapshotData],
    *,
    labeled_assessment_ids: set[int],
    limit: int,
    label_ready_as_of: set[date] | None = None,
) -> list[tuple[str, int]]:
    """Return up to ``limit`` ``(symbol, id)`` pairs: unlabeled, optionally label-ready.

    ``snapshots_newest_first`` must already be newest-first. Assessments without an id,
    already present in ``labeled_assessment_ids``, or (when ``label_ready_as_of`` is set)
    whose ``as_of_trading_date`` is not in that set are omitted.
    """

    if limit <= 0:
        return []

    pairs: list[tuple[str, int]] = []
    for snapshot in snapshots_newest_first:
        if snapshot.id is None:
            continue
        if snapshot.id in labeled_assessment_ids:
            continue
        if (
            label_ready_as_of is not None
            and snapshot.as_of_trading_date not in label_ready_as_of
        ):
            continue
        pairs.append((snapshot.symbol, snapshot.id))
        if len(pairs) >= limit:
            break
    return pairs
