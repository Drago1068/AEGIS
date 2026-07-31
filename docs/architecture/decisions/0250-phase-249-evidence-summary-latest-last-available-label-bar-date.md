# ADR-0250: Phase 249 Evidence Summary Latest Last Available Label Bar Date (draft)

- Status: Proposed (ready after Phase 248; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 245–248 shipped shortfall + required unlock end date (AAPL live shortfall ``20``,
required end ``2026-08-26``, as_of ``2026-07-29``). Operators know how many sessions and
which date unlock, but not **how far stored label-source bars have already advanced** toward
that end — progress vs gap for backfill planning.

Further tip id/as_of scalars are low value; last available label-bar date is the remaining
progress signal.

## Decisions (proposed)

### 1. API

Add ``latest_assessment_last_available_label_bar_date: date | null`` (+ export):

- When latest assessment exists and as_of bar is present on the resolved label bar source,
  return the max stored close date on that source with ``day >= as_of`` (includes as_of when
  no forward closes yet).
- Null when no assessment or ``no_as_of_bar``. Never invent closes.

### 2. Console

``data-testid="evidence-latest-assessment-last-available-label-bar-date"``.

### 3. Out of scope

UI modularization, inventing future closes, default-on calibration, orders.

### 4. Why this next

Shortfall/end date answered “how much / until when?” Last available answers “how far have
bars progressed?” — completes the unlock progress triad without more tip scalars.

## Resume (after Phase 248 gate)

```powershell
# Implement latest_assessment_last_available_label_bar_date (ADR-0250); tests; commit+push; then Phase 250:
# git archive HEAD → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0246-phase-245-evidence-summary-latest-forward-bar-shortfall.md](0246-phase-245-evidence-summary-latest-forward-bar-shortfall.md)
- [0248-phase-247-evidence-summary-latest-required-label-end-date.md](0248-phase-247-evidence-summary-latest-required-label-end-date.md)
- [0249-phase-248-nas-live-verify-phase-247.md](0249-phase-248-nas-live-verify-phase-247.md)
- [0251-phase-250-nas-live-verify-phase-249.md](0251-phase-250-nas-live-verify-phase-249.md)
