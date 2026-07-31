# ADR-0260: Phase 259 Ingest Run Latest Trading Date (draft)

- Status: Proposed (ready after Phase 258; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 257–258 exercised on-demand ingest tip refresh. Live AAPL showed
``stored=0 skipped_existing=501`` with lag/tip unchanged at ``2026-07-29``. Operators
cannot tell whether **providers** lack newer closes or the run merely skipped duplicates
without exposing the max trading date seen in the fetch. Prefer this ingest-run diagnostic
over another evidence-summary scalar or UI modularization.

## Decisions (proposed)

### 1. API

Extend ``IngestionSymbolResult`` (+ domain result) with
``latest_trading_date: date | null``:

- Max ``trading_date`` among bars considered in that symbol’s ingest attempt (accepted,
  skipped-existing, or corrected candidates from the provider fetch — never invent).
- Null when the fetch produced no usable bars / hard error with empty payload.

### 2. Verify

Log ``latest_trading_date`` for the verify symbol on checklist item 124 / successor so
stdout shows provider tip beside store tip.

### 3. Out of scope

New evidence-summary fields, inventing closes, default-on calibration, orders, UI
modularization, forcing provider APIs to return future sessions.

### 4. Why this next

Ingest path is proven; tip stayed flat. Exposing the fetch tip answers “is the store
behind the provider?” without redundant assessment scalars.

## Resume (after Phase 258 gate)

```powershell
# Implement ingest latest_trading_date (ADR-0260); tests; commit+push; then Phase 260:
# git archive HEAD → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0258-phase-257-on-demand-ingest-tip-refresh.md](0258-phase-257-on-demand-ingest-tip-refresh.md)
- [0259-phase-258-nas-live-verify-phase-257.md](0259-phase-258-nas-live-verify-phase-257.md)
- [0261-phase-260-nas-live-verify-phase-259.md](0261-phase-260-nas-live-verify-phase-259.md)
- [0002-phase-1-market-data-ingestion.md](0002-phase-1-market-data-ingestion.md)
