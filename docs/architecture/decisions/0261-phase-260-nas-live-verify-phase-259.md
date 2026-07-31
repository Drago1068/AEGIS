# ADR-0261: Phase 260 NAS Live Verification of Phase 259

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 259 adds ``latest_trading_date`` on ingest symbol results (ADR-0260). Operators need
a verified backend+frontend redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass; ingest logs ``latest_trading_date``
   (checklist item 124).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Live evidence (2026-07-31)

- Revision ``f60cb0b`` (+ verify script ASCII fix); TLS recreate; verify passed.
- AAPL ingest: ``stored=0 skipped_existing=501 latest_trading_date=2026-07-30``;
  store tip unchanged ``pre_tip=2026-07-29 post_tip=2026-07-29``;
  ``stored_bar_calendar_lag_trading_days=2``. Provider tip is **ahead** of store tip —
  actionable divergence for Phase 261.

## Related documents

- [0260-phase-259-ingest-run-latest-trading-date.md](0260-phase-259-ingest-run-latest-trading-date.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
