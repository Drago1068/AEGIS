# ADR-0264: Phase 263 Ingest Primary Tip Diagnostic

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 261–262 advanced evidence tip to the fresher secondary close
(``latest_trading_date_source=polygon``, ``post_tip=2026-07-30``, ``post_lag=1``). Operators
still could not see the **primary** tip beside the winning tip when dual-source ingest
succeeds. Live AAPL can keep ``alpha_vantage`` behind ``polygon`` while assessments mix-fill
forward; diagnosing primary lag needs an explicit primary tip without inventing closes.

## Decisions

### 1. Surface primary tip on ingest results

Add ``primary_latest_trading_date: date | null`` on ``SymbolIngestionResult`` / API:

- Set from the primary provider fetch tip when primary succeeded (empty → null).
- Null when primary errored (even if secondary tip wins).
- Winning tip remains ``latest_trading_date`` / ``latest_trading_date_source``.

Verify logs and the ingest panel show primary tip beside the winning tip.

### 2. Out of scope

Inventing primary closes, switching default primary source, calibration, orders.

## Consequences

Operators can see primary lag (e.g. AV ``2026-07-29`` vs polygon winning tip ``2026-07-30``)
without new evidence-summary fields.

## Resume (Phase 264)

```powershell
# git archive HEAD → NAS; rebuild backend(+frontend) TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0262-phase-261-provider-tip-ahead-of-store.md](0262-phase-261-provider-tip-ahead-of-store.md)
- [0263-phase-262-nas-live-verify-phase-261.md](0263-phase-262-nas-live-verify-phase-261.md)
- [0265-phase-264-nas-live-verify-phase-263.md](0265-phase-264-nas-live-verify-phase-263.md)
