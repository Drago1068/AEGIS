# ADR-0266: Phase 265 Stored Primary Tip Fallback (draft)

- Status: Proposed (ready after Phase 264; do not start until gate approved)
- Date: 2026-07-31

## Context

Phase 263–264 exposed ``primary_latest_trading_date`` from the primary **fetch**. Live AAPL
verify showed ``primary_latest_trading_date=null`` with winning tip ``polygon`` /
``2026-07-30`` because the primary provider failed that run. Stored ``alpha_vantage`` tip
remains ``2026-07-29`` in the DB, but ingest results do not surface it — operators still
need a DB query to see primary lag after a rate-limit.

Prefer a fail-closed stored-tip fallback on the ingest result over another evidence-summary
scalar.

## Decisions (proposed)

### 1. Fallback when primary fetch has no tip

When primary fetch errors or returns empty, set ``primary_latest_trading_date`` from the
max stored close for the configured primary ``source`` (never invent). When primary fetch
succeeds, keep using the fetch tip (current Phase 263 behavior).

### 2. Out of scope

Inventing closes, switching default primary, calibration, orders, UI modularization beyond
existing primary-tip column.

### 3. Why this next

Live null primary tip after rate-limit is the remaining operator gap for primary-vs-winning
attribution.

## Resume (after Phase 264 gate)

```powershell
# Stored primary tip fallback when fetch fails (ADR-0266); tests; commit+push; then Phase 266:
# git archive HEAD → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0264-phase-263-ingest-primary-tip-diagnostic.md](0264-phase-263-ingest-primary-tip-diagnostic.md)
- [0265-phase-264-nas-live-verify-phase-263.md](0265-phase-264-nas-live-verify-phase-263.md)
- [0267-phase-266-nas-live-verify-phase-265.md](0267-phase-266-nas-live-verify-phase-265.md)
