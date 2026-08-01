# ADR-0297: Phase 296 NAS Live Verification of Phase 295

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 295 elevated a primary fetch-fallback data-quality callout from existing
evidence-summary fields (ADR-0296). Operators needed a verified frontend redeploy under
lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``c33bcd5`` via ``git archive``; preserved ``.env.nas``; rebuilt
   frontend TLS compose.
2. ``verify.ps1`` passed (exit 0) against lab HTTPS with insecure + resolve.
3. Alembic ``0009`` / ``head``.

### 2. Live evidence (AAPL, 2026-08-01)

- ``latest_primary_fetch_fallback=full_to_compact``
- ``latest_input_source=alpha_vantage`` ``tip_as_of=2026-07-31``
- Multi-source daily-bars tip still ``fetch_fallback=null`` ``source=polygon``
- Post-ingest ``primary_fetch_fallback=null`` on this run (null OK)
- Upload ≠ verified; retain verify stdout.

## Related documents

- [0296-phase-295-primary-fetch-fallback-callout.md](0296-phase-295-primary-fetch-fallback-callout.md)
- [0298-phase-297-labeling-diagnostics-summary-count.md](0298-phase-297-labeling-diagnostics-summary-count.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
