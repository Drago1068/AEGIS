"""Outcome-label backfill candidate selection (Phase 49 / 57 / 65).

Prefer assessments that lack a default-method label and would pass Phase 13 compute
gates for the resolved label bar source, so tip / already-labeled / false-ready rows
do not consume the operator ``limit`` (ADR-0050, ADR-0058). Among eligible candidates,
prefer ``component_source=mixed`` (newest-first within each tier) so cross-source rows
are labeled sooner for calibration corpus growth (ADR-0066).
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from aegis.domain.research_assessment import (
    ResearchAssessmentSnapshotData,
    ResearchBarInput,
    is_mixed_component_source,
)
from aegis.domain.research_outcome_labels import (
    has_stored_forward_horizon_close,
    is_snapshot_label_ready,
    ready_forward_horizons,
)

# Scan depth for unlabeled label-ready selection (ADR-0058; was 100 in ADR-0050).
BACKFILL_SCAN_LIMIT = 252


def label_ready_as_of_dates(
    bars_newest_first: Sequence[ResearchBarInput],
    *,
    calendar_name: str,
    min_forward_sessions: int | None = None,
    source: str | None = None,
) -> set[date]:
    """Trading dates in ``bars`` that have a stored close on the forward-horizon end.

    When ``source`` is set, only closes from that observation source count (Phase 57).
    """

    close_dates = {
        bar.trading_date
        for bar in bars_newest_first
        if bar.close > 0 and (source is None or bar.source == source)
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
    bars_newest_first: Sequence[ResearchBarInput] | None = None,
    calendar_name: str | None = None,
    label_ready_as_of: set[date] | None = None,
) -> list[tuple[str, int]]:
    """Return up to ``limit`` ``(symbol, id)`` pairs: unlabeled and label-ready.

    ``snapshots_newest_first`` must already be newest-first. Assessments without an id or
    already present in ``labeled_assessment_ids`` are omitted.

    Readiness (when bars + calendar are provided) uses
    :func:`is_snapshot_label_ready` so selection matches compute source gates (ADR-0058).
    ``label_ready_as_of`` remains for tests / callers that precompute a date set; when both
    are provided, snapshot readiness must pass the source-aware check **and** the date set.

    Eligible candidates are ordered mixed-first (Phase 65), then newest-first within each
    tier, before applying ``limit``.
    """

    if limit <= 0:
        return []

    use_source_ready = bars_newest_first is not None and calendar_name is not None

    mixed: list[tuple[str, int]] = []
    other: list[tuple[str, int]] = []
    for snapshot in snapshots_newest_first:
        if snapshot.id is None:
            continue
        if snapshot.id in labeled_assessment_ids:
            continue
        if use_source_ready:
            assert bars_newest_first is not None and calendar_name is not None
            if not is_snapshot_label_ready(
                snapshot,
                bars_newest_first,
                calendar_name=calendar_name,
            ):
                continue
        elif (
            label_ready_as_of is not None
            and snapshot.as_of_trading_date not in label_ready_as_of
        ):
            continue
        pair = (snapshot.symbol, snapshot.id)
        if is_mixed_component_source(snapshot):
            mixed.append(pair)
        else:
            other.append(pair)

    ordered = mixed + other
    return ordered[:limit]


def select_ready_horizons_backfill_candidates(
    snapshots_newest_first: Sequence[ResearchAssessmentSnapshotData],
    *,
    labeled_assessment_ids: set[int],
    limit: int,
    bars_newest_first: Sequence[ResearchBarInput],
    calendar_name: str,
) -> list[tuple[str, int]]:
    """Return up to ``limit`` unlabeled assessments with at least one ready horizon.

    Uses :func:`ready_forward_horizons` so min-horizon-ready tip-blocked rows are eligible
    (ADR-0312). Already-labeled assessments are omitted. Mixed-first, then newest-first.
    Never invents closes.
    """

    if limit <= 0:
        return []

    mixed: list[tuple[str, int]] = []
    other: list[tuple[str, int]] = []
    for snapshot in snapshots_newest_first:
        if snapshot.id is None:
            continue
        if snapshot.id in labeled_assessment_ids:
            continue
        ready = ready_forward_horizons(
            snapshot,
            bars_newest_first,
            calendar_name=calendar_name,
        )
        if not ready:
            continue
        pair = (snapshot.symbol, snapshot.id)
        if is_mixed_component_source(snapshot):
            mixed.append(pair)
        else:
            other.append(pair)

    ordered = mixed + other
    return ordered[:limit]
