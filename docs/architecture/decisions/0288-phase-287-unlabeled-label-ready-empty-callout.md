# ADR-0288: Phase 287 Unlabeled Label-Ready Empty Callout

- Status: Proposed (Phase 286 closed; ready to implement)
- Date: 2026-07-31

## Context

Phases 283–286 elevated tip label-readiness and labeled-corpus freshness lag. Live
verify still shows ``scan_unlabeled_label_ready_count=0`` with unlabeled tip present
(``most_recent_unlabeled_assessment_id`` set; ``most_recent_unlabeled_labelable_as_of``
null). Operators already have the scalars; the research panel does not elevate that
there are currently no unlabeled label-ready candidates in the scan window.

Prefer a fail-closed UI callout over new tip/fallback scalars.

## Decisions

### 1. Empty unlabeled-ready callout

When ``scan_unlabeled_label_ready_count === 0`` and
``most_recent_unlabeled_assessment_id`` is non-null,
``ResearchEvidenceSummarySection`` shows a research-only callout with existing fields
only:

- ``scan_unlabeled_label_ready_count``
- ``most_recent_unlabeled_as_of_trading_date`` when present
- ``most_recent_unlabeled_labelable_as_of_trading_date`` when present (often null)
- ``latest_assessment_forward_bar_shortfall`` / ``latest_assessment_required_label_end_date``
  when tip is also not label-ready

Hidden when unlabeled-ready count is null or ``> 0``, or when there is no unlabeled
assessment id. Never invent labels; never promote to actionable; no orders.

### 2. Out of scope

New API scalars, auto-labeling, inventing closes, orders, calibration default-on.

## Related documents

- [0287-phase-286-nas-live-verify-phase-285.md](0287-phase-286-nas-live-verify-phase-285.md)
- [0289-phase-288-nas-live-verify-phase-287.md](0289-phase-288-nas-live-verify-phase-287.md)
