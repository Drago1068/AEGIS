# ADR-0313: Phase 312 NAS Live Verification of Phase 311 (draft)

- Status: Proposed (pending Phase 311 + live evidence)
- Date: 2026-08-01

## Context

Phase 311 would add ready-horizons outcome-label backfill (ADR-0312). Operators need a
verified NAS redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; rebuild backend (and frontend if UI changed).
2. ``verify.ps1`` pass; retain Phase 310 ready-horizons logs; add Phase 312 backfill evidence.
3. Alembic ``0009`` / ``head`` (or newer if Phase 311 migrates).

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 311 on HEAD: git archive → NAS; rebuild backend (+ frontend if needed); then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0312-phase-311-ready-horizons-backfill.md](0312-phase-311-ready-horizons-backfill.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
