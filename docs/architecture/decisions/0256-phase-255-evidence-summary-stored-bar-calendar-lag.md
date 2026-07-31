# ADR-0256: Phase 255 Evidence Summary Stored Bar Calendar Lag

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 245–254 completed the **max** unlock triad and the **min-horizon** unlock pair.
Live AAPL (``c25e8b6``) shows tip stuck at ``2026-07-29`` with last-available equal to
as_of and shortfalls ``5`` / ``20``. Unlock math is auditable; operators still cannot see
how many **completed exchange sessions** the stored bar tip lags behind the calendar —
distinct from unlock shortfall (sessions until required label end) and from
``scan_labeled_freshness_lag_trading_days`` (labeled as_of vs latest as_of).

A bare ``latest_stored_daily_bar_date`` would usually equal
``latest_assessment_last_available_label_bar_date`` when tip >= as_of — redundant scalar.
Prefer calendar lag.

## Decisions

### 1. API

Add ``stored_bar_calendar_lag_trading_days: int | null`` (+ export):

- Let tip = max stored close date on the resolved label bar source (absolute tip).
- Let reference = prior completed session for ``AEGIS`` ``exchange_calendar_name`` (default
  NYSE) relative to request UTC “now” (``most_recent_trading_day``).
- Lag = non-negative exchange trading-day count from tip through reference (reuse
  ``count_trading_days_strictly_between``; clamp 0 if tip >= reference).
- Null when no assessment / no tip. Never invent closes.

### 2. Console

``data-testid="evidence-stored-bar-calendar-lag-trading-days"``.

### 3. Out of scope

UI modularization, inventing closes, default-on calibration, orders, redundant absolute
tip date that duplicates last-available, forcing provider ingest in this phase.

### 4. Why this next

Unlock answered “how far to label?” Calendar lag answers “how stale is the store vs the
session calendar?” — the product gap blocking tip progress visibility without another
date scalar.

Gate approved by standing instruction ("Proceed and approve from here on out").

## Resume (after Phase 254 gate)

```powershell
# Implement stored_bar_calendar_lag_trading_days (ADR-0256); tests; commit+push; then Phase 256:
# git archive HEAD → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0230-phase-229-evidence-summary-scan-labeled-freshness-lag.md](0230-phase-229-evidence-summary-scan-labeled-freshness-lag.md)
- [0250-phase-249-evidence-summary-latest-last-available-label-bar-date.md](0250-phase-249-evidence-summary-latest-last-available-label-bar-date.md)
- [0255-phase-254-nas-live-verify-phase-253.md](0255-phase-254-nas-live-verify-phase-253.md)
- [0257-phase-256-nas-live-verify-phase-255.md](0257-phase-256-nas-live-verify-phase-255.md)
