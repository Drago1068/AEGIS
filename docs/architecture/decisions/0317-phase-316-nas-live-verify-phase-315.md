# ADR-0317: Phase 316 NAS Live Verification of Phase 315

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 315 exposed complete vs partial labeled assessment counts on evidence-summary
(ADR-0316). Operators needed a verified NAS redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``2ad567e`` via ``git archive``; preserved ``.env.nas``; rebuilt
   backend + frontend TLS; waited ``/ready`` via docker-exec urllib.
2. ``verify.ps1`` passed. Live AAPL evidence-summary:
   ``complete=67`` ``partial=0`` ``labeled=67`` (complete+partial == labeled). Tip still
   calendar-blocked (``min_horizon_shortfall=5``).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0316-phase-315-partial-complete-label-coverage.md](0316-phase-315-partial-complete-label-coverage.md)
- [0318-phase-317-partial-label-upgrade-callout.md](0318-phase-317-partial-label-upgrade-callout.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
