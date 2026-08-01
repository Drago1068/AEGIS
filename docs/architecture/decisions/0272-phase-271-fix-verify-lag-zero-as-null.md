# ADR-0272: Phase 271 Fix Verify Lag Zero Displayed as Null

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 269–270 advanced the store tip to ``2026-07-31`` via Polygon ``/prev``. Live verify
logged ``post_lag=null`` after tip catch-up even though calendar lag should be ``0`` when
tip equals the prior completed session. PowerShell ``$postLag -eq ""`` is true for
numeric ``0`` (``""`` coerces to ``0``), so the verify script mis-labels lag zero as null.

## Decisions

### 1. Null-only check for lag logging

In ``verify.ps1``, treat only ``$null`` as missing for
``stored_bar_calendar_lag_trading_days`` (pre and post ingest). Print ``0`` when lag is
zero. API semantics unchanged.

### 2. Out of scope

API schema changes, inventing closes, orders, broad rewrite of all ``-eq ""`` helpers.

## Consequences

- Operators see truthful ``post_lag=0`` after tip catch-up.
- Phase 272 live-verifies the display.

## Related documents

- [0271-phase-270-nas-live-verify-phase-269.md](0271-phase-270-nas-live-verify-phase-269.md)
- [0273-phase-272-nas-live-verify-phase-271.md](0273-phase-272-nas-live-verify-phase-271.md)
