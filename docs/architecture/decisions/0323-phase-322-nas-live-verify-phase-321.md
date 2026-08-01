# ADR-0323: Phase 322 NAS Live Verification of Phase 321

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 321 elevated a ready-horizons CTA when min-horizon shortfall is zero while tip is
not fully label-ready (ADR-0322). Operators needed a verified NAS frontend redeploy under
lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``2103beb`` via ``git archive``; preserved ``.env.nas``; rebuilt
   frontend TLS; confirmed backend ``/ready``.
2. ``verify.ps1`` passed. Live AAPL still ``min_shortfall=5`` ``tip_ready=False``
   (``min_end=2026-08-07``); CTA elevates when shortfall=0 (unit-tested).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0322-phase-321-min-horizon-unlock-cta.md](0322-phase-321-min-horizon-unlock-cta.md)
- [0324-phase-323-full-horizon-unlock-cta.md](0324-phase-323-full-horizon-unlock-cta.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
