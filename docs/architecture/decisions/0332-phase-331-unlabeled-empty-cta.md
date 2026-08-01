# ADR-0332: Phase 331 Unlabeled-Empty Ready-Horizon CTA

- Status: Accepted
- Date: 2026-08-01

## Context

Phases 287–288 surface an unlabeled label-ready empty callout when
``scan_unlabeled_label_ready_count === 0`` and an unlabeled assessment exists. Live NAS
shows ``ready_count=0`` with ``unlabeled_id`` set, but the callout did not point at
existing opt-in ready-horizon backfill. Tip max-horizon remains calendar-blocked;
ready-horizon backfill can still catch earlier unlocks without inventing bars.

## Decisions

### 1. Unlabeled-empty CTA (UI-only)

- When the existing unlabeled-empty callout is active, add a research-only CTA line
  pointing at ``Backfill ready-horizon labels`` (no auto-run).
- Source of truth: existing evidence-summary fields only; no new API scalars.
- Callout CTA ``data-testid="evidence-unlabeled-ready-empty-callout-cta"``.

### 2. Out of scope

Auto-backfill, inventing bars, orders, changing readiness counts, changing unlock CTAs.

## Related documents

- [0331-phase-330-nas-live-verify-phase-329.md](0331-phase-330-nas-live-verify-phase-329.md)
- [0288-phase-287-unlabeled-label-ready-empty-callout.md](0288-phase-287-unlabeled-label-ready-empty-callout.md)
- [0333-phase-332-nas-live-verify-phase-331.md](0333-phase-332-nas-live-verify-phase-331.md)
