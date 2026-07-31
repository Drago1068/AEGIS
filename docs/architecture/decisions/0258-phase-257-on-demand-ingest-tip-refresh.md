# ADR-0258: Phase 257 On-Demand Ingest Tip Refresh (draft)

- Status: Proposed (ready after Phase 256; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 255–256 shipped ``stored_bar_calendar_lag_trading_days``. Live AAPL shows lag
``2`` with tip ``2026-07-29`` while unlock shortfalls remain ``5`` / ``20``. Operators can
see calendar staleness; the product gap is **advancing the store** via existing
``POST /market-data/ingest`` (+ post-ingest research when enabled), not another evidence
scalar.

Prefer this ops/product refresh over UI modularization or redundant tip dates.

## Decisions (proposed)

### 1. Scope

1. Document and exercise authenticated on-demand ingest for the verify symbol (and
   optionally the watchlist) under lab TLS.
2. After ingest (+ post-ingest research when configured), re-read evidence-summary:
   expect tip / ``stored_bar_calendar_lag_trading_days`` to improve when providers have
   newer closes (null/unchanged OK if upstream has no new sessions — never invent).
3. Extend ``verify.ps1`` / ``verify.sh`` with a checklist item that runs ingest and logs
   pre/post lag (fail only on HTTP/contract errors, not on unchanged lag).
4. No new evidence-summary fields in this phase.

### 2. Out of scope

New providers, inventing closes, default-on calibration, orders, UI modularization,
weakening fail-closed gates.

### 3. Why this next

Calendar lag diagnosed the gap. Tip refresh is the actionable next step so unlock
shortfall/last-available can move without more diagnostics.

## Resume (after Phase 256 gate)

```powershell
# Implement Phase 257 ingest tip refresh (ADR-0258); verify checklist; commit+push; then Phase 258:
# git archive HEAD → NAS; rebuild backend+frontend TLS if needed; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0256-phase-255-evidence-summary-stored-bar-calendar-lag.md](0256-phase-255-evidence-summary-stored-bar-calendar-lag.md)
- [0257-phase-256-nas-live-verify-phase-255.md](0257-phase-256-nas-live-verify-phase-255.md)
- [0259-phase-258-nas-live-verify-phase-257.md](0259-phase-258-nas-live-verify-phase-257.md)
- [0009-phase-8-scheduled-research.md](0009-phase-8-scheduled-research.md)
