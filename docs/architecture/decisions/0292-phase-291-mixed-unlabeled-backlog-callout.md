# ADR-0292: Phase 291 Mixed-Unlabeled Backlog Callout

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 283–290 elevated and grouped tip label-readiness, freshness lag, and empty
unlabeled-ready diagnostics. Live verify still shows ``mixed_unlabeled_assessment_count=7``
(with ``mixed_component_source_assessment_count=26``). Operators already have the
scalars; the labeling-diagnostics group did not elevate mixed-source unlabeled backlog.

Prefer a fail-closed UI callout inside the existing diagnostics group over new API
scalars.

## Decisions

### 1. Mixed-unlabeled backlog callout

When ``mixed_unlabeled_assessment_count`` is a positive integer, show a research-only
callout inside ``evidence-labeling-diagnostics`` (group appears when any labeling
trigger fires, including this one) using existing fields only:

- ``mixed_unlabeled_assessment_count``
- ``mixed_component_source_assessment_count`` when present
- ``mixed_labeled_assessment_count`` when present
- ``latest_mixed_label_bar_source`` when present

Hidden when count is null or ``<= 0``. Never invent labels; no orders.

### 2. Out of scope

New API scalars, auto-labeling, inventing closes, orders, calibration default-on.

## Related documents

- [0291-phase-290-nas-live-verify-phase-289.md](0291-phase-290-nas-live-verify-phase-289.md)
- [0293-phase-292-nas-live-verify-phase-291.md](0293-phase-292-nas-live-verify-phase-291.md)
