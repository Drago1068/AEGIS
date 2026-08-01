# ADR-0265: Phase 264 NAS Live Verification of Phase 263

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 263 added ingest ``primary_latest_trading_date`` (ADR-0264). Operators needed a
verified TLS redeploy with live evidence.

## Decisions

### 1. Scope completed

1. Deployed ``25adb4f`` TLS; rebuilt backend + frontend.
2. ``verify.ps1`` passed; ingest contract includes ``primary_latest_trading_date``.
3. Alembic ``0009`` / ``head``.

### 2. Live evidence (AAPL)

```
latest_trading_date=2026-07-30 latest_trading_date_source=polygon
primary_latest_trading_date=null
pre_lag=1 post_lag=1 pre_tip=2026-07-30 post_tip=2026-07-30
```

Primary fetch contributed no tip this run (null is correct fail-closed attribution); winning
tip remained polygon. Store tip / lag unchanged. Remaining gap: when primary fetch fails,
operators still cannot see the **stored** primary tip without a DB inspect.

### 3. Upload ≠ verified

Retain verify stdout as acceptance evidence.

## Related documents

- [0264-phase-263-ingest-primary-tip-diagnostic.md](0264-phase-263-ingest-primary-tip-diagnostic.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
