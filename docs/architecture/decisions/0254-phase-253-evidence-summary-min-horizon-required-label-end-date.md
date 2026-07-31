# ADR-0254: Phase 253 Evidence Summary Min-Horizon Required Label End Date (draft)

- Status: Proposed (ready after Phase 252; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 251–252 shipped min-horizon shortfall (AAPL live ``5`` vs max ``20``). Operators know
how many sessions remain for earliest unlock but not **which trading date** unlocks the
minimum horizon — the calendar companion to min shortfall (mirroring max end date).

## Decisions (proposed)

### 1. API

Add ``latest_assessment_min_horizon_required_label_end_date: date | null`` (+ export):

- Same as ``latest_assessment_required_label_end_date`` but for
  ``horizons=(min(FORWARD_HORIZON_SESSIONS),)``.
- Null when no assessment / ``no_as_of_bar``. Never invent closes.

### 2. Console

``data-testid="evidence-latest-assessment-min-horizon-required-label-end-date"``.

### 3. Out of scope

UI modularization, inventing closes, default-on calibration, orders, multi-horizon maps.

### 4. Why this next

Min shortfall answered “how many for earliest?” End date answers “until which session?” —
completes the min-horizon unlock pair beside the max triad.

## Resume (after Phase 252 gate)

```powershell
# Implement latest_assessment_min_horizon_required_label_end_date (ADR-0254); tests; commit+push; then Phase 254:
# git archive HEAD → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0248-phase-247-evidence-summary-latest-required-label-end-date.md](0248-phase-247-evidence-summary-latest-required-label-end-date.md)
- [0252-phase-251-evidence-summary-min-horizon-forward-bar-shortfall.md](0252-phase-251-evidence-summary-min-horizon-forward-bar-shortfall.md)
- [0253-phase-252-nas-live-verify-phase-251.md](0253-phase-252-nas-live-verify-phase-251.md)
- [0255-phase-254-nas-live-verify-phase-253.md](0255-phase-254-nas-live-verify-phase-253.md)
