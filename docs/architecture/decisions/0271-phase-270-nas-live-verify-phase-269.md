# ADR-0271: Phase 270 NAS Live Verification of Phase 269

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 269 merged Polygon ``/prev`` when range aggregates lag (ADR-0270). Operators needed
a verified backend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``f1ed164`` TLS; rebuilt backend.
2. ``verify.ps1`` passed; alembic ``0009`` / ``head``.
3. Live AAPL ingest evidence:
   ``stored=1``, ``latest_trading_date=2026-07-31``,
   ``latest_trading_date_source=polygon``, tip ``2026-07-30`` → ``2026-07-31``.

### 2. Upload ≠ verified

Retain verify stdout as acceptance evidence.

## Related documents

- [0270-phase-269-advance-store-tip-current-session.md](0270-phase-269-advance-store-tip-current-session.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
