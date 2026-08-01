# ADR-0311: Phase 310 NAS Live Verification of Phase 309

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 309 added an explicit ready-horizons outcome-label path when tip is blocked
(ADR-0310). Operators needed a verified backend+frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``b5b6e86`` via ``git archive``; preserved ``.env.nas``;
   rebuilt backend + frontend TLS; waited ``/ready`` via docker-exec urllib.
2. ``verify.ps1`` passed. Live AAPL ready-horizons:
   ``POST .../assessments/213/outcome-labels/ready-horizons`` → ``422``
   ``reason=insufficient_forward_bars`` (tip still blocked;
   ``min_horizon_shortfall=5``). Unauth → ``401``.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0310-phase-309-min-horizon-label-path.md](0310-phase-309-min-horizon-label-path.md)
- [0312-phase-311-ready-horizons-backfill.md](0312-phase-311-ready-horizons-backfill.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
