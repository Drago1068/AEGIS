# ADR-0327: Phase 326 NAS Live Verification of Phase 325

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 325 elevated a mixed-unlabeled backlog CTA pointing at ``Backfill outcome labels``
(ADR-0326). Operators needed a verified NAS frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``e7ace4b`` via ``git archive``; preserved ``.env.nas``; rebuilt
   frontend TLS; confirmed backend ``/ready``.
2. ``verify.ps1`` passed. Live AAPL ``mixed_unlabeled=7`` elevates CTA
   (``use_toolbar=Backfill outcome labels``; unit-tested).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0326-phase-325-mixed-unlabeled-backlog-cta.md](0326-phase-325-mixed-unlabeled-backlog-cta.md)
- [0328-phase-327-freshness-lag-cta.md](0328-phase-327-freshness-lag-cta.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
