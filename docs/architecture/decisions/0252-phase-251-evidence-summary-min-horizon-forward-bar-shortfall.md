# ADR-0252: Phase 251 Evidence Summary Min-Horizon Forward Bar Shortfall

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 245–250 completed the **max**-horizon unlock triad (shortfall / required end /
last available). Live AAPL shows max shortfall ``20`` with last available equal to as_of.
Operators still lack **when the earliest horizon** (``min(FORWARD_HORIZON_SESSIONS)``,
currently 5) becomes labelable — partial unlock precedes full max-horizon readiness.

Further tip id/as_of scalars are low value; min-horizon shortfall is the next actionable
unlock signal.

## Decisions

### 1. API

Add ``latest_assessment_min_horizon_forward_bar_shortfall: int | null`` (+ export):

- Same semantics as ``latest_assessment_forward_bar_shortfall`` but for
  ``horizons=(min(FORWARD_HORIZON_SESSIONS),)``.
- ``0`` when min-horizon label-ready; null when no assessment / ``no_as_of_bar``.
  Never invent.

### 2. Console

``data-testid="evidence-latest-assessment-min-horizon-forward-bar-shortfall"``.

### 3. Out of scope

UI modularization, inventing closes, default-on calibration, orders, multi-horizon maps.

### 4. Why this next

Max triad answered full unlock. Min shortfall answers “when can *any* horizon label?” —
earlier backfill signal without redundant tip scalars.

Gate approved by standing instruction ("Proceed and approve from here on out").

## Resume (after Phase 250 gate)

```powershell
# Implement latest_assessment_min_horizon_forward_bar_shortfall (ADR-0252); tests; commit+push; then:
# git archive HEAD → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0246-phase-245-evidence-summary-latest-forward-bar-shortfall.md](0246-phase-245-evidence-summary-latest-forward-bar-shortfall.md)
- [0250-phase-249-evidence-summary-latest-last-available-label-bar-date.md](0250-phase-249-evidence-summary-latest-last-available-label-bar-date.md)
- [0251-phase-250-nas-live-verify-phase-249.md](0251-phase-250-nas-live-verify-phase-249.md)
- [0253-phase-252-nas-live-verify-phase-251.md](0253-phase-252-nas-live-verify-phase-251.md)
