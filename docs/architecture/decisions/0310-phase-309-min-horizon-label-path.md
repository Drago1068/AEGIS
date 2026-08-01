# ADR-0310: Phase 309 Min-Horizon Label Path When Tip Blocked

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 307–308 shipped a labeling frontier readout. Live AAPL remains tip-blocked
(``forward_bar_shortfall=20``, ``required_end=2026-08-28``) while the min horizon is closer
(``min_horizon_shortfall=5``, ``min_horizon_end=2026-08-07``). Full
``POST .../outcome-labels`` fail-closes the whole assessment when the tip/max horizon lacks
forward bars, so operators could not persist research-only ``forward_return_5`` labels when
that horizon alone is ready.

## Decisions

### 1. Explicit ready-horizons path

- Domain: ``ready_forward_horizons`` + ``OutcomeLabelService.label_assessment_ready_horizons``
  compute/persist only individually ready horizons from stored bars (never invent closes).
- API: ``POST /research/{symbol}/assessments/{id}/outcome-labels/ready-horizons`` — opt-in;
  full-label endpoint unchanged.
- UI: ``Compute ready-horizon labels`` toolbar action (research-only).
- Fail-closed ``422`` with ``insufficient_forward_bars`` / ``no_as_of_bar`` when none ready.
- Append-only: full-label path remains available later when tip unlocks.

### 2. Out of scope

Live orders, inventing forward bars, default-on auto-labeling, changing backfill to upgrade
partial→full automatically, calibration default-on, evidence-panel callout stacking.

## Related documents

- [0309-phase-308-nas-live-verify-phase-307.md](0309-phase-308-nas-live-verify-phase-307.md)
- [0311-phase-310-nas-live-verify-phase-309.md](0311-phase-310-nas-live-verify-phase-309.md)
- [../research-scoring.md](../research-scoring.md)
