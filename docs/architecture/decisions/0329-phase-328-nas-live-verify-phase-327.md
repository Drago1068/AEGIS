# ADR-0329: Phase 328 NAS Live Verification of Phase 327

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 327 elevated a freshness-lag CTA pointing at ``Backfill ready-horizon labels``
(ADR-0328). Operators needed a verified NAS frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``00d8853`` via ``git archive``; preserved ``.env.nas``; rebuilt
   frontend TLS; confirmed backend ``/ready``.
2. ``verify.ps1`` passed. Live AAPL ``lag=121`` elevates CTA
   (``use_toolbar=Backfill ready-horizon labels``; unit-tested).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0328-phase-327-freshness-lag-cta.md](0328-phase-327-freshness-lag-cta.md)
- [0330-phase-329-primary-fetch-fallback-cta.md](0330-phase-329-primary-fetch-fallback-cta.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
