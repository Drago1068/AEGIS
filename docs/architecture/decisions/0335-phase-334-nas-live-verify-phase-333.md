# ADR-0335: Phase 334 NAS Live Verification of Phase 333 (draft)

- Status: Proposed (pending Phase 333 + live evidence)
- Date: 2026-08-01

## Context

Phase 333 would elevate a tip-not-ready CTA pointing at ``Compute ready-horizon labels``
(ADR-0334). Operators need a verified NAS frontend redeploy under lab TLS.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; rebuild frontend.
2. ``verify.ps1`` pass; live tip_not_ready expected to elevate CTA (unit-tested).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 333 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0334-phase-333-tip-not-ready-cta.md](0334-phase-333-tip-not-ready-cta.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
