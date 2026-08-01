# ADR-0309: Phase 308 NAS Live Verification of Phase 307

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 307 added a labeling frontier readout from evidence-summary fields (ADR-0308).
Operators needed a verified frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``7c03852`` via ``git archive``; preserved ``.env.nas``;
   rebuilt frontend TLS; waited ``/ready`` via docker-exec urllib.
2. ``verify.ps1`` passed. Live AAPL frontier bundle:
   ``tip_ready=False`` ``forward_shortfall=20`` ``required_end=2026-08-28``
   ``min_horizon_shortfall=5`` ``min_horizon_end=2026-08-07``
   ``last_available=2026-07-31``.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0308-phase-307-labeling-frontier-readout.md](0308-phase-307-labeling-frontier-readout.md)
- [0310-phase-309-min-horizon-label-path.md](0310-phase-309-min-horizon-label-path.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
