# ADR-0313: Phase 312 NAS Live Verification of Phase 311

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 311 added ready-horizons outcome-label backfill (ADR-0312). Operators needed a
verified backend+frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``e0cc736`` via ``git archive``; preserved ``.env.nas``;
   rebuilt backend + frontend TLS; waited ``/ready`` via docker-exec urllib.
2. ``verify.ps1`` passed. Live AAPL ready-horizons backfill:
   ``assessment_count=15`` ``persisted=15`` ``skipped=0``. Tip single-shot path still
   ``422`` (``min_horizon_shortfall=5``).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0312-phase-311-ready-horizons-backfill.md](0312-phase-311-ready-horizons-backfill.md)
- [0314-phase-313-full-horizon-upgrade-backfill.md](0314-phase-313-full-horizon-upgrade-backfill.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
