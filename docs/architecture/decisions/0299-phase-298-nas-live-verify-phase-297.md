# ADR-0299: Phase 298 NAS Live Verification of Phase 297 (draft)

- Status: Proposed (pending Phase 297 + live evidence)
- Date: 2026-08-01

## Context

Phase 297 would show an active-count badge on the labeling-diagnostics summary
(ADR-0298). Operators need a verified frontend redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate frontend.
2. ``verify.ps1`` pass; Phase 290/294 trigger logs still present; UI unit-tested count.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 297 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0298-phase-297-labeling-diagnostics-summary-count.md](0298-phase-297-labeling-diagnostics-summary-count.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
