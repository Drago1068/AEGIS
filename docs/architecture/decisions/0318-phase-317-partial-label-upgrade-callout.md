# ADR-0318: Phase 317 Partial-Label Upgrade Backlog Callout

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 315–316 exposed ``partial_labeled_assessment_count`` on evidence-summary. When
partials are present operators need an elevated labeling-diagnostics callout so the
upgrade backlog is not missed among dense summary fields.

## Decisions

### 1. Diagnostics callout

- When ``partial_labeled_assessment_count > 0``, surface a research-only callout inside the
  existing labeling-diagnostics group (same pattern as mixed-unlabeled / freshness lag).
- Copy states upgrade eligibility once max horizon unlocks; no auto-run.
- Counts remain the source of truth; callout is display-only from existing fields.

### 2. Out of scope

Inventing bars, auto full-horizon upgrade, changing backfill selection, orders,
expanding the ≤100 scan window, new API scalars.

## Related documents

- [0316-phase-315-partial-complete-label-coverage.md](0316-phase-315-partial-complete-label-coverage.md)
- [0317-phase-316-nas-live-verify-phase-315.md](0317-phase-316-nas-live-verify-phase-315.md)
- [0319-phase-318-nas-live-verify-phase-317.md](0319-phase-318-nas-live-verify-phase-317.md)
- [0320-phase-319-outcome-label-horizon-coverage-badge.md](0320-phase-319-outcome-label-horizon-coverage-badge.md)
