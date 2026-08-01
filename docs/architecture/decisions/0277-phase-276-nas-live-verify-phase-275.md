# ADR-0277: Phase 276 NAS Live Verification of Phase 275

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 275 surfaced ``primary_fetch_fallback`` on ingest symbol results (ADR-0276).
Operators needed a verified backend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``d4cafbc`` TLS; rebuilt backend.
2. ``verify.ps1`` passed; alembic ``0009`` / ``head``.
3. Live AAPL ingest evidence:
   ``primary_latest_trading_date=2026-07-31``,
   ``latest_trading_date_source=alpha_vantage``,
   ``primary_fetch_fallback=full_to_compact``.

### 2. Upload ≠ verified

Retain verify stdout as acceptance evidence.

## Related documents

- [0276-phase-275-ingest-primary-fetch-fallback.md](0276-phase-275-ingest-primary-fetch-fallback.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
