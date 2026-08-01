# ADR-0314: Phase 313 Full-Horizon Upgrade Backfill for Partial Labels

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 311–312 grew the ``forward_return_5`` corpus via ready-horizons backfill
(``persisted=15`` on live AAPL). Those append-only rows marked assessments as “labeled” for
full-horizon backfill selection, so when the tip/max horizon later unlocks,
``POST .../outcome-labels/backfill`` would skip them.

## Decisions

### 1. Complete-horizon skip set

- ``label_covers_configured_horizons`` / ``assessment_ids_with_complete_labels`` treat an
  assessment as complete only when the latest default-method label includes all
  ``FORWARD_HORIZON_SESSIONS`` keys.
- Full backfill selection uses that complete set (not any-label). Partial ready-horizons
  rows remain eligible once full gates pass; new complete rows are append-only.
- Ready-horizons backfill still skips any-labeled assessments (unchanged).

### 2. Out of scope

Changing ready-horizons backfill semantics, inventing bars, orders, evidence-panel
stacking, default-on scheduling.

## Related documents

- [0313-phase-312-nas-live-verify-phase-311.md](0313-phase-312-nas-live-verify-phase-311.md)
- [0315-phase-314-nas-live-verify-phase-313.md](0315-phase-314-nas-live-verify-phase-313.md)
- [0312-phase-311-ready-horizons-backfill.md](0312-phase-311-ready-horizons-backfill.md)
