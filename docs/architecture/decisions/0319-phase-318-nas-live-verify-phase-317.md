# ADR-0319: Phase 318 NAS Live Verification of Phase 317

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 317 added a labeling-diagnostics callout when ``partial_labeled_assessment_count > 0``
(ADR-0318). Operators needed a verified NAS frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``1f4b719`` via ``git archive``; preserved ``.env.nas``; rebuilt
   frontend TLS; confirmed backend ``/ready``.
2. ``verify.ps1`` passed. Live AAPL: ``partial=0`` ``complete=66`` ``labeled=66`` (callout
   elevates when count>0; unit-tested). Tip still calendar-blocked
   (``min_horizon_shortfall=5``).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0318-phase-317-partial-label-upgrade-callout.md](0318-phase-317-partial-label-upgrade-callout.md)
- [0320-phase-319-outcome-label-horizon-coverage-badge.md](0320-phase-319-outcome-label-horizon-coverage-badge.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
