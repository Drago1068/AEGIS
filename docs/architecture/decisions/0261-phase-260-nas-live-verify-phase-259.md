# ADR-0261: Phase 260 NAS Live Verification of Phase 259 (draft)

- Status: Proposed (pending Phase 259 + live evidence)
- Date: 2026-07-31

## Context

Phase 259 would add ``latest_trading_date`` on ingest symbol results (ADR-0260). Operators
need a verified backend redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend (frontend optional if unchanged).
2. ``verify.ps1`` / ``verify.sh`` pass; ingest result logs ``latest_trading_date``.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 259 on HEAD: git archive → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0260-phase-259-ingest-run-latest-trading-date.md](0260-phase-259-ingest-run-latest-trading-date.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
