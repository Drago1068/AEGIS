# ADR-0327: Phase 326 NAS Live Verification of Phase 325 (draft)

- Status: Proposed (pending Phase 325 + live evidence)
- Date: 2026-08-01

## Context

Phase 325 would elevate a mixed-unlabeled backlog CTA pointing at existing backfill
toolbar actions (ADR-0326). Operators need a verified NAS frontend redeploy under lab TLS.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; rebuild frontend.
2. ``verify.ps1`` pass; live ``mixed_unlabeled>0`` expected to elevate CTA (unit-tested).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 325 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0326-phase-325-mixed-unlabeled-backlog-cta.md](0326-phase-325-mixed-unlabeled-backlog-cta.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
