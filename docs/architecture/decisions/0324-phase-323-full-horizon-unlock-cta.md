# ADR-0324: Phase 323 Full-Horizon Unlock Outcome-Label CTA (draft)

- Status: Proposed
- Date: 2026-08-01

## Context

Phase 321–322 elevate a ready-horizons CTA when the min horizon unlocks while tip remains
blocked. The symmetric gap: when tip becomes fully label-ready
(``latest_assessment_is_label_ready === true``) but still has no outcome label
(``latest_outcome_label_id == null``), nothing elevates the existing
``Compute outcome labels`` toolbar action.

## Decisions (proposed)

### 1. Tip-ready unlabeled CTA (UI-only)

- When ``latest_assessment_is_label_ready === true`` and ``latest_outcome_label_id == null``,
  elevate a research-only labeling-diagnostics callout pointing at
  ``Compute outcome labels`` (no auto-run).
- Source of truth: existing evidence-summary fields only; no new API scalars.

### 2. Out of scope

Auto-labeling, inventing bars, orders, changing backfill, ready-horizons CTA changes.

## Resume

```powershell
# Implement Phase 323 full-horizon unlock CTA; tests; commit+push; then:
# git archive HEAD → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0323-phase-322-nas-live-verify-phase-321.md](0323-phase-322-nas-live-verify-phase-321.md)
- [0322-phase-321-min-horizon-unlock-cta.md](0322-phase-321-min-horizon-unlock-cta.md)
- [0325-phase-324-nas-live-verify-phase-323.md](0325-phase-324-nas-live-verify-phase-323.md)
