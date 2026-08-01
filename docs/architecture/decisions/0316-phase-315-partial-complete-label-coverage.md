# ADR-0316: Phase 315 Partial vs Complete Label Coverage Counts (draft)

- Status: Proposed
- Date: 2026-08-01

## Context

Phase 313–314 keep partial ready-horizons labels upgrade-eligible for full-horizon
backfill, but evidence-summary still reports a single ``labeled_assessment_count`` that
treats any default-method label as labeled. Operators cannot see how many scan rows are
complete (all configured horizons) versus partial (upgrade backlog) without inspecting
individual label payloads.

## Decisions (proposed)

### 1. Evidence-summary coverage split

- Add research-only counts derived from latest default-method labels in the scan window:
  - ``complete_labeled_assessment_count`` — latest label covers all
    ``FORWARD_HORIZON_SESSIONS`` keys (``label_covers_configured_horizons``).
  - ``partial_labeled_assessment_count`` — has a latest label but is not complete.
- Keep existing ``labeled_assessment_count`` / ``unlabeled_assessment_count`` semantics
  (any-label) so prior consumers stay stable.
- Console surfaces the new counts; state remains ``research_only``.

### 2. Out of scope

Inventing bars, auto full-horizon upgrade scheduling, orders, changing backfill
selection, actionable promotion.

## Resume

```powershell
# Implement Phase 315 evidence-summary partial/complete counts; tests; commit+push; then:
# git archive HEAD → NAS; rebuild backend (+ frontend if UI); then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0314-phase-313-full-horizon-upgrade-backfill.md](0314-phase-313-full-horizon-upgrade-backfill.md)
- [0315-phase-314-nas-live-verify-phase-313.md](0315-phase-314-nas-live-verify-phase-313.md)
- [0317-phase-316-nas-live-verify-phase-315.md](0317-phase-316-nas-live-verify-phase-315.md)
