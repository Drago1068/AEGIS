# ADR-0272: Phase 271 Fix Verify Lag Zero Displayed as Null (draft)

- Status: Proposed (ready after Phase 270; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 269–270 advanced the store tip to ``2026-07-31`` via Polygon ``/prev``. Live verify
logged ``post_lag=null`` after tip catch-up even though calendar lag should be ``0`` when
tip equals the prior completed session. PowerShell ``$postLag -eq ""`` is true for
numeric ``0`` (``""`` coerces to ``0``), so the verify script mis-labels lag zero as null.

Prefer fixing the verify display so operators trust lag=0 evidence over more tip scalars.

## Decisions (proposed)

### 1. Null-only check for lag logging

In ``verify.ps1`` (and ``verify.sh`` if mirrored), treat only ``$null`` as missing for
``stored_bar_calendar_lag_trading_days``; print ``0`` when lag is zero. Do not change
API semantics.

### 2. Out of scope

API schema changes, inventing closes, orders.

## Resume (after Phase 270 gate)

```powershell
# Fix verify lag=0 displayed as null (ADR-0272); commit+push; then Phase 272:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0271-phase-270-nas-live-verify-phase-269.md](0271-phase-270-nas-live-verify-phase-269.md)
- [0273-phase-272-nas-live-verify-phase-271.md](0273-phase-272-nas-live-verify-phase-271.md)
