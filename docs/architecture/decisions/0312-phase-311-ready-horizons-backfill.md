# ADR-0312: Phase 311 Ready-Horizons Label Backfill

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 309–310 shipped an explicit per-assessment ready-horizons label path. Live tip
AAPL still fail-closes (``min_horizon_shortfall=5`` until ~2026-08-07). Historical
assessments may already be min-horizon ready while remaining unlabeled. Operators need a
research-only batch path to grow the ``forward_return_5`` corpus without waiting for
tip/max-horizon unlock and without auto-running on schedule.

## Decisions

### 1. Ready-horizons backfill

- Selection: ``select_ready_horizons_backfill_candidates`` — unlabeled only; eligible when
  ``ready_forward_horizons`` is non-empty (mixed-first).
- Runner: ``run_ready_horizons_outcome_labels_after_assessments`` applies
  ``label_assessment_ready_horizons`` per candidate; per-row fail-closed.
- API: ``POST /research/{symbol}/outcome-labels/backfill/ready-horizons`` (opt-in; full
  backfill unchanged).
- UI: ``Backfill ready-horizon labels`` toolbar action.

### 2. Out of scope

Default-on scheduling, inventing bars, silent mutation of full-label backfill, orders,
evidence-panel callout stacking, auto-upgrade of partial→full labels.

## Related documents

- [0311-phase-310-nas-live-verify-phase-309.md](0311-phase-310-nas-live-verify-phase-309.md)
- [0313-phase-312-nas-live-verify-phase-311.md](0313-phase-312-nas-live-verify-phase-311.md)
- [0310-phase-309-min-horizon-label-path.md](0310-phase-309-min-horizon-label-path.md)
