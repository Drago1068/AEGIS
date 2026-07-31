# ADR-0259: Phase 258 NAS Live Verification of Phase 257

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 257 adds on-demand ingest tip refresh to the NAS verify gate (ADR-0258). Operators
need live evidence that authenticated ingest ran and pre/post lag/tip were observed.

## Decisions

### 1. Scope

1. Scripts-only OK (no runtime image change).
2. ``verify.ps1`` / ``verify.sh`` pass including checklist item 124.
3. Retain pre/post ``stored_bar_calendar_lag_trading_days`` (and tip / as_of) in stdout
   (unchanged OK).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Live evidence (2026-07-31)

- Revision ``c84524f``; scripts-only; verify passed.
- AAPL: authenticated ``POST /market-data/ingest`` → 200;
  ``stored=0 skipped_existing=501``; tip refresh
  ``pre_lag=2 post_lag=2 pre_tip=2026-07-29 post_tip=2026-07-29`` (unchanged OK —
  providers returned no newer closes than the store tip).

## Related documents

- [0258-phase-257-on-demand-ingest-tip-refresh.md](0258-phase-257-on-demand-ingest-tip-refresh.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
