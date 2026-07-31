# ADR-0257: Phase 256 NAS Live Verification of Phase 255

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 255 adds ``stored_bar_calendar_lag_trading_days`` (ADR-0256). Operators need a
verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass.
3. Evidence-summary includes ``stored_bar_calendar_lag_trading_days`` (null/0 OK;
   checklist item 123).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Live evidence (2026-07-31)

- Revision ``9259c16``; TLS recreate backend+frontend; verify passed.
- AAPL: ``stored_bar_calendar_lag_trading_days=2`` (tip
  ``latest_assessment_last_available_label_bar_date=2026-07-29`` vs prior completed
  session on verify day); min end ``2026-08-05`` / max end ``2026-08-26``;
  shortfalls ``5`` / ``20``.

## Related documents

- [0256-phase-255-evidence-summary-stored-bar-calendar-lag.md](0256-phase-255-evidence-summary-stored-bar-calendar-lag.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
