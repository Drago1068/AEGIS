# ADR-0311: Phase 310 NAS Live Verification of Phase 309 (draft)

- Status: Proposed (pending Phase 309 + live evidence)
- Date: 2026-08-01

## Context

Phase 309 would add an explicit min-horizon / ready-horizons outcome-label path when the tip
is still blocked (ADR-0310). Operators need a verified NAS redeploy under lab TLS after that
lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; rebuild backend (and frontend if UI changed).
2. ``verify.ps1`` pass; retain Phase 308 frontier logs; add Phase 310 ready-horizons evidence.
3. Alembic ``0009`` / ``head`` (or newer if Phase 309 migrates).

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 309 on HEAD: git archive → NAS; rebuild backend (+ frontend if needed); then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0310-phase-309-min-horizon-label-path.md](0310-phase-309-min-horizon-label-path.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
