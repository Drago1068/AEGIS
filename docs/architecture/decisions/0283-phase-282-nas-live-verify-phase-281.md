# ADR-0283: Phase 282 NAS Live Verification of Phase 281

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 281 surfaced ``fetch_fallback`` on daily-bars responses and the bars table
(ADR-0282). Operators needed a verified backend+frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``58023db`` TLS; rebuilt backend + frontend.
2. ``verify.ps1`` passed; alembic ``0009`` / ``head``.
3. Live AAPL daily-bars tip:
   ``fetch_fallback=full_to_compact``,
   ``trading_date=2026-07-31``, ``source=alpha_vantage``.

### 2. Upload ≠ verified

Retain verify stdout as acceptance evidence.

## Related documents

- [0282-phase-281-daily-bars-fetch-fallback.md](0282-phase-281-daily-bars-fetch-fallback.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
