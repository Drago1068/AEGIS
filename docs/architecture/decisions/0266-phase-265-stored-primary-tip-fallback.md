# ADR-0266: Phase 265 Stored Primary Tip Fallback

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 263–264 exposed ``primary_latest_trading_date`` from the primary **fetch**. Live AAPL
verify showed ``primary_latest_trading_date=null`` with winning tip ``polygon`` /
``2026-07-30`` because the primary provider failed that run. Stored ``alpha_vantage`` tip
remained ``2026-07-29`` in the DB, but ingest results did not surface it.

## Decisions

### 1. Fallback when primary fetch has no tip

When primary fetch errors or returns empty (no ``latest_trading_date``), set
``primary_latest_trading_date`` from ``get_max_trading_date(primary_source, symbol)`` —
max stored close for that source (never invent). When primary fetch succeeds with a tip,
keep using the fetch tip (Phase 263).

### 2. Out of scope

Inventing closes, switching default primary, calibration, orders, UI modularization beyond
the existing primary-tip column.

## Consequences

Operators see stored primary lag after rate-limits without a DB query. Null remains when
the primary store is also empty.

## Resume (Phase 266)

```powershell
# git archive HEAD → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0264-phase-263-ingest-primary-tip-diagnostic.md](0264-phase-263-ingest-primary-tip-diagnostic.md)
- [0265-phase-264-nas-live-verify-phase-263.md](0265-phase-264-nas-live-verify-phase-263.md)
- [0267-phase-266-nas-live-verify-phase-265.md](0267-phase-266-nas-live-verify-phase-265.md)
