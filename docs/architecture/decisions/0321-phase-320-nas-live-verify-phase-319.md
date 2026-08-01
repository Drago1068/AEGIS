# ADR-0321: Phase 320 NAS Live Verification of Phase 319

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 319 added complete/partial horizon coverage badges on outcome-label history
(ADR-0320). Operators needed a verified NAS frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``36f9a8a`` via ``git archive``; preserved ``.env.nas``; rebuilt
   frontend TLS; confirmed backend ``/ready``.
2. ``verify.ps1`` passed with Phase 320 horizon coverage badge log (UI unit-tested). Tip
   still calendar-blocked (``min_horizon_shortfall=5``; ``min_horizon_end=2026-08-07``).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0320-phase-319-outcome-label-horizon-coverage-badge.md](0320-phase-319-outcome-label-horizon-coverage-badge.md)
- [0322-phase-321-min-horizon-unlock-cta.md](0322-phase-321-min-horizon-unlock-cta.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
