# ADR-0314: Phase 313 Full-Horizon Upgrade Backfill for Partial Labels (draft)

- Status: Proposed (Phase 312 closed; ready to implement after gate approval)
- Date: 2026-08-01

## Context

Phase 311–312 grew the ``forward_return_5`` corpus via ready-horizons backfill
(``persisted=15`` on live AAPL). Those append-only rows mark assessments as “labeled” for
full-horizon backfill selection, so when the tip/max horizon later unlocks,
``POST .../outcome-labels/backfill`` will skip them and never append a full
``forward_return_5``+``forward_return_20`` row unless operators hit the single-assessment
full path manually.

## Decisions

### 1. Treat incomplete latest labels as full-backfill candidates

When selecting full-horizon backfill candidates, treat an assessment as already complete
only if its latest default-method label includes **all** configured
``FORWARD_HORIZON_SESSIONS`` keys. Partially labeled (ready-horizons-only) rows remain
eligible for ``label_assessment`` once full gates pass. Fail-closed; research-only; never
invent bars; do not auto-schedule.

### 2. Out of scope

Changing ready-horizons backfill, inventing bars, orders, evidence-panel stacking,
default-on scheduling.

## Resume

```powershell
# Implement Phase 313 full-horizon upgrade for partial labels; tests; commit+push; then:
# git archive HEAD → NAS; rebuild backend (+ frontend if UI); then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0313-phase-312-nas-live-verify-phase-311.md](0313-phase-312-nas-live-verify-phase-311.md)
- [0315-phase-314-nas-live-verify-phase-313.md](0315-phase-314-nas-live-verify-phase-313.md)
- [0312-phase-311-ready-horizons-backfill.md](0312-phase-311-ready-horizons-backfill.md)
