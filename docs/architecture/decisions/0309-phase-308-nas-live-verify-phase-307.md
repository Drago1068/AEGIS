# ADR-0309: Phase 308 NAS Live Verification of Phase 307 (draft)

- Status: Proposed (pending Phase 307 + live evidence)
- Date: 2026-08-01

## Context

Phase 307 would add a labeling frontier readout from evidence-summary fields
(ADR-0308). Operators need a verified frontend redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate frontend.
2. ``verify.ps1`` pass; retain Phase 284/298 shortfall logs; UI unit-tested frontier.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 307 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0308-phase-307-labeling-frontier-readout.md](0308-phase-307-labeling-frontier-readout.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
