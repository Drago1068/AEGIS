# ADR-0325: Phase 324 NAS Live Verification of Phase 323 (draft)

- Status: Proposed (pending Phase 323 + live evidence)
- Date: 2026-08-01

## Context

Phase 323 would elevate a full-horizon outcome-label CTA when tip is label-ready but
unlabeled (ADR-0324). Operators need a verified NAS frontend redeploy under lab TLS.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; rebuild frontend.
2. ``verify.ps1`` pass; UI unit-tested CTA (live tip may still be not ready until max
   horizon unlocks ~2026-08-28).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 323 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0324-phase-323-full-horizon-unlock-cta.md](0324-phase-323-full-horizon-unlock-cta.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
