# ADR-0273: Phase 272 NAS Live Verification of Phase 271

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 271 fixed verify logging so calendar lag ``0`` is not shown as ``null`` (ADR-0272).

## Decisions

### 1. Scope completed

1. ``verify.ps1`` from ``HEAD`` against lab TLS (script-only; no backend rebuild required).
2. Live evidence: ``stored_bar_calendar_lag_trading_days=0``,
   ``pre_lag=0 post_lag=0``, tip ``2026-07-31``.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain verify stdout as acceptance evidence.

## Related documents

- [0272-phase-271-fix-verify-lag-zero-as-null.md](0272-phase-271-fix-verify-lag-zero-as-null.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
