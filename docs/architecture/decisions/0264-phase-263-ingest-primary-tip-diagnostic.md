# ADR-0264: Phase 263 Ingest Primary Tip Diagnostic (draft)

- Status: Proposed (ready after Phase 262; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 261–262 advanced evidence tip to the fresher secondary close
(``latest_trading_date_source=polygon``, ``post_tip=2026-07-30``, ``post_lag=1``). Operators
still cannot see the **primary** tip beside the winning tip when dual-source ingest
succeeds. Live AAPL can keep ``alpha_vantage`` behind ``polygon`` while assessments mix-fill
forward; diagnosing primary lag needs an explicit primary tip without inventing closes.

Prefer a small ingest diagnostic over another evidence-summary scalar or UI modularization.

## Decisions (proposed)

### 1. Surface primary tip on ingest results

Add ``primary_latest_trading_date: date | null`` (and optionally keep existing max tip /
``latest_trading_date_source``) on ``SymbolIngestionResult`` / API so verify and the ingest
panel can show primary vs winning tip when they diverge.

### 2. Out of scope

Inventing primary closes, switching default primary source, calibration, orders.

### 3. Why this next

Tip advancement works; remaining operator gap is primary-vs-secondary tip attribution
beyond the single winning tip source.

## Resume (after Phase 262 gate)

```powershell
# Add ingest primary tip diagnostic (ADR-0264); tests; commit+push; then Phase 264:
# git archive HEAD → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0262-phase-261-provider-tip-ahead-of-store.md](0262-phase-261-provider-tip-ahead-of-store.md)
- [0263-phase-262-nas-live-verify-phase-261.md](0263-phase-262-nas-live-verify-phase-261.md)
- [0265-phase-264-nas-live-verify-phase-263.md](0265-phase-264-nas-live-verify-phase-263.md)
