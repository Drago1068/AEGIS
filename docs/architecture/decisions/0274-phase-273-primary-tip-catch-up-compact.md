# ADR-0274: Phase 273 Primary Tip Catch-Up When Full Output Is Premium-Gated (draft)

- Status: Proposed (ready after Phase 272; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 269–272 closed Polygon tip catch-up (``/prev``) and truthful lag=0 display. Live
AAPL still shows ``primary_latest_trading_date=2026-07-29`` while polygon tip is
``2026-07-31``. Alpha Vantage ``outputsize=full`` remains premium-gated (rate-limit /
failover), so primary store tip lags even when compact daily history might expose a newer
primary close.

Prefer a fail-closed primary tip catch-up (compact retry or equivalent real AV closes)
over inventing primary bars from polygon.

## Decisions (proposed)

### 1. Fail-closed primary tip

When primary ``full`` fetch fails with a premium/rate-limit gate, attempt a compact
primary fetch (or documented equivalent) solely to advance primary tip with real AV
closes. Never copy polygon closes onto ``alpha_vantage`` provenance.

### 2. Out of scope

Inventing closes, silent provenance swaps, default-on calibration, orders.

## Resume (after Phase 272 gate)

```powershell
# Primary tip catch-up when AV full is premium-gated (ADR-0274); tests; commit+push; then Phase 274:
# git archive HEAD → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0273-phase-272-nas-live-verify-phase-271.md](0273-phase-272-nas-live-verify-phase-271.md)
- [0275-phase-274-nas-live-verify-phase-273.md](0275-phase-274-nas-live-verify-phase-273.md)
- [0266-phase-265-stored-primary-tip-fallback.md](0266-phase-265-stored-primary-tip-fallback.md)
