# ADR-0275: Phase 274 NAS Live Verification of Phase 273

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 273 added Alpha Vantage full→compact tip catch-up with a free-tier delay
(ADR-0274). Operators needed a verified backend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``99e0c8e`` TLS; rebuilt backend.
2. ``verify.ps1`` passed; alembic ``0009`` / ``head``.
3. Live AAPL ingest evidence:
   ``primary_latest_trading_date=2026-07-31``,
   ``latest_trading_date_source=alpha_vantage``,
   ``stored=2`` / ``corrected=1`` (compact fallback landed real AV closes).

### 2. Upload ≠ verified

Retain verify stdout as acceptance evidence.

## Related documents

- [0274-phase-273-primary-tip-catch-up-compact.md](0274-phase-273-primary-tip-catch-up-compact.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
