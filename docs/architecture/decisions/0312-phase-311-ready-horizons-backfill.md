# ADR-0312: Phase 311 Ready-Horizons Label Backfill (draft)

- Status: Proposed (Phase 310 closed; ready to implement after gate approval)
- Date: 2026-08-01

## Context

Phase 309–310 shipped an explicit per-assessment ready-horizons label path. Live tip
AAPL still fail-closes (``min_horizon_shortfall=5`` until ~2026-08-07). Historical
assessments may already be min-horizon ready while remaining unlabeled (or only
partially labeled). Operators need a research-only batch path to grow the
``forward_return_5`` corpus without waiting for tip/max-horizon unlock and without
auto-running on schedule.

## Decisions

### 1. Ready-horizons backfill

Add an authenticated opt-in backfill that scans recent assessments and applies
``label_assessment_ready_horizons`` (or equivalent) per candidate: persist when at
least one horizon is ready; fail-closed skip otherwise. Prefer unlabeled rows; do not
invent bars; keep ``research_only``; never place orders. Full-horizon backfill remains
unchanged.

### 2. Out of scope

Default-on scheduling, inventing bars, silent mutation of the full-label backfill,
orders, evidence-panel callout stacking.

## Resume

```powershell
# Implement Phase 311 ready-horizons label backfill; tests; commit+push; then:
# git archive HEAD → NAS; rebuild backend (+ frontend if UI); then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0311-phase-310-nas-live-verify-phase-309.md](0311-phase-310-nas-live-verify-phase-309.md)
- [0313-phase-312-nas-live-verify-phase-311.md](0313-phase-312-nas-live-verify-phase-311.md)
- [0310-phase-309-min-horizon-label-path.md](0310-phase-309-min-horizon-label-path.md)
