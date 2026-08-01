# ADR-0307: Phase 306 NAS Live Verification of Phase 305 (draft)

- Status: Proposed (pending Phase 305 + live evidence)
- Date: 2026-08-01

## Context

Phase 305 would default assessment history to distinct-as_of rows (ADR-0306).
Operators need a verified frontend redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate frontend.
2. ``verify.ps1`` pass; retain Phase 300/302/304 chart logs; UI unit-tested list mode.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 305 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0306-phase-305-distinct-as-of-assessment-history.md](0306-phase-305-distinct-as-of-assessment-history.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
