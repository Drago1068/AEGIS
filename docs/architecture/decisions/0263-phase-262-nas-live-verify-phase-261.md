# ADR-0263: Phase 262 NAS Live Verification of Phase 261

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 261 dual-source ingest tip catch-up and cross-source fill tip extension (ADR-0262)
needed live evidence under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``d092cf2`` TLS; rebuilt backend + frontend.
2. ``verify.ps1`` passed.
3. Alembic ``0009`` / ``head``.

### 2. Live evidence (AAPL)

- Ingest: ``stored=0 skipped_existing=500 latest_trading_date=2026-07-30
  latest_trading_date_source=polygon``.
- Tip refresh: ``pre_lag=2 post_lag=1 pre_tip=2026-07-29 post_tip=2026-07-30
  pre_as_of=2026-07-29 post_as_of=2026-07-30``.
- Provider tip advanced store / assessment tip without inventing closes. Remaining lag=1
  is fail-closed (expected session ahead of stored tip).

### 3. Upload ≠ verified

Retain verify stdout as acceptance evidence.

## Related documents

- [0262-phase-261-provider-tip-ahead-of-store.md](0262-phase-261-provider-tip-ahead-of-store.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
