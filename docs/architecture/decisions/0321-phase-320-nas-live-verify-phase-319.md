# ADR-0321: Phase 320 NAS Live Verification of Phase 319 (draft)

- Status: Proposed (pending Phase 319 + live evidence)
- Date: 2026-08-01

## Context

Phase 319 would add a complete/partial horizon coverage badge on outcome-label history
rows (ADR-0320). Operators need a verified NAS frontend redeploy under lab TLS after that
lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; rebuild frontend.
2. ``verify.ps1`` pass; retain Phase 318 partial-count logs; UI unit-tested badge evidence.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 319 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0320-phase-319-outcome-label-horizon-coverage-badge.md](0320-phase-319-outcome-label-horizon-coverage-badge.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
