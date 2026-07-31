# ADR-0248: Phase 247 Evidence Summary Latest Required Label End Date (draft)

- Status: Proposed (ready after Phase 246; do not start until gate approved)
- Date: 2026-07-31

## Context

Phase 245–246 shipped ``latest_assessment_forward_bar_shortfall`` (AAPL live ``20``).
Operators know how many sessions remain but not **which trading date** unlocks max-horizon
labeling — the companion calendar date to the shortfall count for backfill planning.

Further tip scalars (duplicate ids/as_ofs) are low value; the required end date is actionable
beside shortfall.

## Decisions (proposed)

### 1. API

Add ``latest_assessment_required_label_end_date: date | null`` (+ export):

- When latest assessment exists and as_of bar is present, return
  ``forward_horizon_end_date(as_of, max(FORWARD_HORIZON_SESSIONS))``.
- Null when no assessment or ``no_as_of_bar`` (date not applicable). Never invent market
  closes; this is a calendar projection from stored as_of only.

### 2. Console

``data-testid="evidence-latest-assessment-required-label-end-date"``.

### 3. Out of scope

UI modularization, inventing future closes, default-on calibration, orders.

### 4. Why this next

Shortfall answered “how many sessions?” End date answers “until which session date?” —
the remaining operator gap for unlock timing.

## Resume (after Phase 246 gate)

```powershell
# Implement latest_assessment_required_label_end_date (ADR-0248); tests; commit+push; then:
# git archive HEAD → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

Gate approved by standing instruction ("Proceed and approve from here on out").

## Related documents

- [0246-phase-245-evidence-summary-latest-forward-bar-shortfall.md](0246-phase-245-evidence-summary-latest-forward-bar-shortfall.md)
- [0247-phase-246-nas-live-verify-phase-245.md](0247-phase-246-nas-live-verify-phase-245.md)
- [0249-phase-248-nas-live-verify-phase-247.md](0249-phase-248-nas-live-verify-phase-247.md)
