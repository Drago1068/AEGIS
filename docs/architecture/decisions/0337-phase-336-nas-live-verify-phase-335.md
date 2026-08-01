# ADR-0337: Phase 336 NAS Live Verification of Phase 335

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 335 elevated a partial-labeled upgrade CTA pointing at ``Backfill outcome labels``
(ADR-0336). Operators needed a verified NAS frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``ace6781`` via ``git archive``; preserved ``.env.nas``; rebuilt
   frontend TLS; confirmed backend ``/ready``.
2. ``verify.ps1`` passed. Live AAPL ``partial=0`` (CTA elevates when count>0;
   unit-tested).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0336-phase-335-partial-labeled-upgrade-cta.md](0336-phase-335-partial-labeled-upgrade-cta.md)
- [0338-phase-337-calendar-unlock-ops-checkpoint.md](0338-phase-337-calendar-unlock-ops-checkpoint.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
