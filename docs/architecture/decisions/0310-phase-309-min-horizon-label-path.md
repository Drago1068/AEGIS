# ADR-0310: Phase 309 Min-Horizon Label Path When Tip Blocked (draft)

- Status: Proposed (Phase 308 closed; ready to implement after gate approval)
- Date: 2026-08-01

## Context

Phase 307–308 shipped a labeling frontier readout. Live AAPL remains tip-blocked
(``forward_bar_shortfall=20``, ``required_end=2026-08-28``) while the min horizon is closer
(``min_horizon_shortfall=5``, ``min_horizon_end=2026-08-07``). Current
``POST .../outcome-labels`` fail-closes the whole assessment when the tip/max horizon lacks
forward bars, so operators cannot persist research-only ``forward_return_5`` labels when that
horizon alone is ready.

That is the next **product** gap (domain labeling path), not more evidence-panel UI stacking.

## Decisions

### 1. Min-horizon (ready-horizons) label path

When an assessment is tip-blocked for the full horizon set but one or more configured
horizons are individually label-ready, allow an explicit research-only request to compute
and append labels **only for ready horizons**, fail-closed for unreadies. Do not invent
bars; do not auto-run; keep ``research_only``; never place orders.

Prefer reusing existing readiness/shortfall helpers; add the smallest API/UI surface needed
(explicit opt-in, not silent partial success on the full-label endpoint unless ADR proves
safe).

### 2. Out of scope

Live orders, inventing forward bars, default-on auto-labeling, calibration default-on,
additional evidence-panel callout stacking, watchlist multi-symbol polish.

## Resume

```powershell
# Implement Phase 309 min-horizon ready-horizons label path; tests; commit+push; then:
# git archive HEAD → NAS; rebuild backend (+ frontend if UI); then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0309-phase-308-nas-live-verify-phase-307.md](0309-phase-308-nas-live-verify-phase-307.md)
- [0311-phase-310-nas-live-verify-phase-309.md](0311-phase-310-nas-live-verify-phase-309.md)
- [../research-scoring.md](../research-scoring.md)
