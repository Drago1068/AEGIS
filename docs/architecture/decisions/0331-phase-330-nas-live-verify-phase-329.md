# ADR-0331: Phase 330 NAS Live Verification of Phase 329

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 329 elevated a primary fetch-fallback CTA pointing at ``Run ingest`` (ADR-0330).
Operators needed a verified NAS frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``786d28b`` via ``git archive``; preserved ``.env.nas``; rebuilt
   frontend TLS; confirmed backend ``/ready``.
2. ``verify.ps1`` passed. Live AAPL ``fallback=full_to_compact`` elevates CTA
   (``use_console=Run ingest``; unit-tested).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0330-phase-329-primary-fetch-fallback-cta.md](0330-phase-329-primary-fetch-fallback-cta.md)
- [0332-phase-331-unlabeled-empty-cta.md](0332-phase-331-unlabeled-empty-cta.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
