# ADR-0333: Phase 332 NAS Live Verification of Phase 331

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 331 elevated an unlabeled-empty CTA pointing at ``Backfill ready-horizon labels``
(ADR-0332). Operators needed a verified NAS frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``99e5676`` via ``git archive``; preserved ``.env.nas``; rebuilt
   frontend TLS; confirmed backend ``/ready``.
2. ``verify.ps1`` passed. Live AAPL ``ready_count=0`` ``unlabeled_id=246`` elevates CTA
   (``use_toolbar=Backfill ready-horizon labels``; unit-tested).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0332-phase-331-unlabeled-empty-cta.md](0332-phase-331-unlabeled-empty-cta.md)
- [0334-phase-333-tip-not-ready-cta.md](0334-phase-333-tip-not-ready-cta.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
