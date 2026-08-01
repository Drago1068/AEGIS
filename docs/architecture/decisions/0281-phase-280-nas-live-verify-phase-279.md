# ADR-0281: Phase 280 NAS Live Verification of Phase 279

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 279 surfaced ``latest_primary_fetch_fallback`` on evidence-summary from the
stored primary tip ``raw_payload`` (ADR-0280). Operators needed a verified
backend+frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``13ff029`` TLS; rebuilt backend + frontend.
2. ``verify.ps1`` passed; alembic ``0009`` / ``head``.
3. Live AAPL evidence-summary:
   ``latest_primary_fetch_fallback=full_to_compact``,
   ``stored_bar_calendar_lag_trading_days=0``.

### 2. Upload ≠ verified

Retain verify stdout as acceptance evidence.

## Related documents

- [0280-phase-279-evidence-summary-primary-fetch-fallback.md](0280-phase-279-evidence-summary-primary-fetch-fallback.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
