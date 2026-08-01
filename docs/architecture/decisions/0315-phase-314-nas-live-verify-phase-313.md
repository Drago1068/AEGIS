# ADR-0315: Phase 314 NAS Live Verification of Phase 313

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 313 made full-horizon backfill skip only complete-horizon latest labels so partial
ready-horizons rows remain upgrade-eligible (ADR-0314). Operators needed a verified NAS
redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``9810086`` via ``git archive``; preserved ``.env.nas``; rebuilt
   backend TLS (frontend unchanged); waited ``/ready`` via docker-exec urllib.
2. ``verify.ps1`` passed (``LIVE VERIFICATION PASSED``). Phase 314 checklist log present:
   complete-horizon skip / upgrade eligibility (unit-tested). Tip still calendar-blocked
   (``min_horizon_shortfall=5``); full-horizon upgrade persists may be ``0`` until max
   horizon unlocks — expected.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0314-phase-313-full-horizon-upgrade-backfill.md](0314-phase-313-full-horizon-upgrade-backfill.md)
- [0316-phase-315-partial-complete-label-coverage.md](0316-phase-315-partial-complete-label-coverage.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
