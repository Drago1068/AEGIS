# ADR-0267: Phase 266 NAS Live Verification of Phase 265 (draft)

- Status: Proposed (pending Phase 265 + live evidence)
- Date: 2026-07-31

## Context

Phase 265 would fall back to stored primary tip when primary fetch fails (ADR-0266).
Operators need a verified backend redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend (frontend if unchanged OK).
2. ``verify.ps1`` pass; ingest logs ``primary_latest_trading_date`` non-null when primary
   store has a tip even if primary fetch fails (null OK only when store also empty).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 265 on HEAD: git archive → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0266-phase-265-stored-primary-tip-fallback.md](0266-phase-265-stored-primary-tip-fallback.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
