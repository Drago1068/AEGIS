# ADR-0333: Phase 332 NAS Live Verification of Phase 331 (draft)

- Status: Proposed (pending Phase 331 + live evidence)
- Date: 2026-08-01

## Context

Phase 331 would elevate an unlabeled-empty CTA pointing at ready-horizon backfill
(ADR-0332). Operators need a verified NAS frontend redeploy under lab TLS.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; rebuild frontend.
2. ``verify.ps1`` pass; live ``ready_count=0`` + unlabeled id expected to elevate CTA
   (unit-tested).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 331 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0332-phase-331-unlabeled-empty-cta.md](0332-phase-331-unlabeled-empty-cta.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
