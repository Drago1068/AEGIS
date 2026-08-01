# ADR-0335: Phase 334 NAS Live Verification of Phase 333

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 333 elevated a tip-not-ready CTA pointing at ``Compute ready-horizon labels``
(ADR-0334). Operators needed a verified NAS frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``ccdadbe`` via ``git archive``; preserved ``.env.nas``; rebuilt
   frontend TLS; confirmed backend ``/ready``.
2. ``verify.ps1`` passed. Live AAPL ``tip_ready=False`` ``forward_shortfall=20`` elevates
   CTA (``use_toolbar=Compute ready-horizon labels``; unit-tested).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0334-phase-333-tip-not-ready-cta.md](0334-phase-333-tip-not-ready-cta.md)
- [0336-phase-335-partial-labeled-upgrade-cta.md](0336-phase-335-partial-labeled-upgrade-cta.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
