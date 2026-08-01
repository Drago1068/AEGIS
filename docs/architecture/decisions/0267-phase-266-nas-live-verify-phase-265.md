# ADR-0267: Phase 266 NAS Live Verification of Phase 265

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 265 added stored primary tip fallback when primary fetch has no tip (ADR-0266).
Operators needed a verified TLS backend redeploy with live evidence.

## Decisions

### 1. Scope completed

1. Deployed ``7b71a87`` TLS; rebuilt backend.
2. ``verify.ps1`` passed.
3. Alembic ``0009`` / ``head``.

### 2. Live evidence (AAPL)

```
latest_trading_date=2026-07-30 latest_trading_date_source=polygon
primary_latest_trading_date=2026-07-29
pre_lag=1 post_lag=1 pre_tip=2026-07-30 post_tip=2026-07-30
```

Stored primary tip now surfaces beside the winning secondary tip without inventing closes.
Remaining calendar lag=1 is fail-closed (expected session ahead of store tip).

### 3. Upload ≠ verified

Retain verify stdout as acceptance evidence.

## Related documents

- [0266-phase-265-stored-primary-tip-fallback.md](0266-phase-265-stored-primary-tip-fallback.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
