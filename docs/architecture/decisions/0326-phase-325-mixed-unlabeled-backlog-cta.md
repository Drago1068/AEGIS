# ADR-0326: Phase 325 Mixed-Unlabeled Backlog CTA

- Status: Accepted
- Date: 2026-08-01

## Context

Phases 291–292 surface a mixed-source unlabeled backlog callout when
``mixed_unlabeled_assessment_count > 0``. Live NAS currently shows ``mixed_unlabeled=7``,
but the callout did not point operators at the existing opt-in backfill toolbar actions.
Tip full-horizon labeling remains calendar-blocked until ~2026-08-28; mixed backlog is
actionable now without inventing bars.

## Decisions

### 1. Mixed-unlabeled CTA (UI-only)

- When ``mixed_unlabeled_assessment_count > 0`` (existing callout), add a research-only
  CTA line pointing at ``Backfill outcome labels`` (no auto-run).
- Source of truth: existing evidence-summary fields only; no new API scalars.
- Callout CTA ``data-testid="evidence-mixed-unlabeled-backlog-callout-cta"``.

### 2. Out of scope

Auto-backfill, inventing bars, orders, changing prefer-mixed / backfill semantics,
changing unlock CTAs.

## Related documents

- [0325-phase-324-nas-live-verify-phase-323.md](0325-phase-324-nas-live-verify-phase-323.md)
- [0292-phase-291-mixed-unlabeled-backlog-callout.md](0292-phase-291-mixed-unlabeled-backlog-callout.md)
- [0327-phase-326-nas-live-verify-phase-325.md](0327-phase-326-nas-live-verify-phase-325.md)
