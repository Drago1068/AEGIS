# ADR-0275: Phase 274 NAS Live Verification of Phase 273 (draft)

- Status: Proposed (pending Phase 273 + live evidence)
- Date: 2026-07-31

## Context

Phase 273 would catch up primary tip when Alpha Vantage ``full`` is premium-gated
(ADR-0274). Operators need a verified backend redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend.
2. ``verify.ps1`` pass; ingest logs ``primary_latest_trading_date`` advanced when compact
   AV closes exist (still may lag polygon; never invent).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 273 on HEAD: git archive → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0274-phase-273-primary-tip-catch-up-compact.md](0274-phase-273-primary-tip-catch-up-compact.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
