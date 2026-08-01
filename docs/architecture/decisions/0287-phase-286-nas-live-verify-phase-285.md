# ADR-0287: Phase 286 NAS Live Verification of Phase 285 (draft)

- Status: Proposed (pending Phase 285 + live evidence)
- Date: 2026-07-31

## Context

Phase 285 would surface a labeled-corpus freshness-lag callout from existing
evidence-summary fields (ADR-0286). Operators need a verified frontend redeploy under
lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate frontend.
2. ``verify.ps1`` pass; evidence-summary still reports
   ``scan_labeled_freshness_lag_trading_days`` (+ related as_of dates; UI unit-tested).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 285 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0286-phase-285-labeled-freshness-lag-callout.md](0286-phase-285-labeled-freshness-lag-callout.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
