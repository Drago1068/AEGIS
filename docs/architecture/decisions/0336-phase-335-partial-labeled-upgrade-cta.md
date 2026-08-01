# ADR-0336: Phase 335 Partial-Labeled Upgrade CTA

- Status: Accepted
- Date: 2026-08-01

## Context

Phases 317–318 surface a partial-labeled upgrade callout when
``partial_labeled_assessment_count > 0``. Live NAS currently shows ``partial=0``, but when
partials return (min-horizon labels before max horizon unlocks), the callout did not point
at existing opt-in full-horizon backfill. Completes the labeling-diagnostics CTA set.

## Decisions

### 1. Partial-labeled CTA (UI-only)

- When ``partial_labeled_assessment_count > 0`` (existing callout), add a research-only
  CTA line pointing at ``Backfill outcome labels`` (no auto-run).
- Source of truth: existing evidence-summary fields only; no new API scalars.
- Callout CTA ``data-testid="evidence-partial-labeled-upgrade-callout-cta"``.

### 2. Out of scope

Auto-backfill, inventing bars, orders, changing complete/partial counts, changing unlock CTAs.

## Related documents

- [0335-phase-334-nas-live-verify-phase-333.md](0335-phase-334-nas-live-verify-phase-333.md)
- [0318-phase-317-partial-label-upgrade-callout.md](0318-phase-317-partial-label-upgrade-callout.md)
- [0337-phase-336-nas-live-verify-phase-335.md](0337-phase-336-nas-live-verify-phase-335.md)
- [0338-phase-337-calendar-unlock-ops-checkpoint.md](0338-phase-337-calendar-unlock-ops-checkpoint.md)
