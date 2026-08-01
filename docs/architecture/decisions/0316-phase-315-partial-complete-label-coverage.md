# ADR-0316: Phase 315 Partial vs Complete Label Coverage Counts

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 313–314 keep partial ready-horizons labels upgrade-eligible for full-horizon
backfill, but evidence-summary still reported a single ``labeled_assessment_count`` that
treats any default-method label as labeled. Operators could not see how many scan rows are
complete (all configured horizons) versus partial (upgrade backlog).

## Decisions

### 1. Evidence-summary coverage split

- ``complete_labeled_assessment_count`` — latest default-method label covers all
  ``FORWARD_HORIZON_SESSIONS`` keys (``label_covers_configured_horizons`` / ADR-0314).
- ``partial_labeled_assessment_count`` — has a latest label but is not complete
  (``labeled − complete``).
- Existing ``labeled_assessment_count`` / ``unlabeled_assessment_count`` keep any-label
  semantics.
- Console surfaces both counts; state remains ``research_only``.

### 2. Out of scope

Inventing bars, auto full-horizon upgrade scheduling, orders, changing backfill
selection, actionable promotion.

## Related documents

- [0314-phase-313-full-horizon-upgrade-backfill.md](0314-phase-313-full-horizon-upgrade-backfill.md)
- [0315-phase-314-nas-live-verify-phase-313.md](0315-phase-314-nas-live-verify-phase-313.md)
- [0317-phase-316-nas-live-verify-phase-315.md](0317-phase-316-nas-live-verify-phase-315.md)
