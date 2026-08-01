# ADR-0291: Phase 290 NAS Live Verification of Phase 289 (draft)

- Status: Proposed (pending Phase 289 + live evidence)
- Date: 2026-07-31

## Context

Phase 289 would group the three labeling diagnostic callouts under one research-only
region (ADR-0290). Operators need a verified frontend redeploy under lab TLS after that
lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate frontend.
2. ``verify.ps1`` pass; existing Phase 284/286/288 field bundles still log; UI unit-tested
   group wrapper.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 289 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0290-phase-289-labeling-diagnostics-group.md](0290-phase-289-labeling-diagnostics-group.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
