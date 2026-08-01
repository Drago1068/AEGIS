# ADR-0315: Phase 314 NAS Live Verification of Phase 313 (draft)

- Status: Proposed (pending Phase 313 + live evidence)
- Date: 2026-08-01

## Context

Phase 313 would allow full-horizon backfill to upgrade partial ready-horizon labels
(ADR-0314). Operators need a verified NAS redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; rebuild backend (and frontend if UI changed).
2. ``verify.ps1`` pass; retain Phase 312 ready-horizons backfill logs; add Phase 314 evidence.
3. Alembic ``0009`` / ``head`` (or newer if Phase 313 migrates).

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 313 on HEAD: git archive → NAS; rebuild backend (+ frontend if needed); then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0314-phase-313-full-horizon-upgrade-backfill.md](0314-phase-313-full-horizon-upgrade-backfill.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
