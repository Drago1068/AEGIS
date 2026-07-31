# ADR-0231: Phase 230 NAS Live Verification of Phase 229

- Status: Proposed (pending Phase 229 + live evidence)
- Date: 2026-07-31

## Context

Phase 229 adds ``scan_labeled_freshness_lag_trading_days`` on evidence summary
(ADR-0230). Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab
TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``scan_labeled_freshness_lag_trading_days``
   (null OK when either as_of date missing; checklist item 110).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math beyond the lag diagnostic, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 229 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
# Expect: OK Phase 230 scan_labeled_freshness_lag_trading_days=… (AAPL non-null; ~119 for current corpus)
```

## Related documents

- [0230-phase-229-evidence-summary-scan-labeled-freshness-lag.md](0230-phase-229-evidence-summary-scan-labeled-freshness-lag.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
