# ADR-0006: Phase 5 Daily Bar Charts

- Status: Accepted
- Date: 2026-07-28

## Context

Phase 3 (ADR-0004) deliberately rendered stored daily bars as an HTML table and deferred
chart libraries. Phase 4 (ADR-0005) added operator authentication so protected market-data
routes are fail-closed. Operators now need a visual OHLC view of the same authenticated
daily-bar payload without introducing new APIs, indicators, or domain scoring.

## Decisions

### 1. Data: existing authenticated daily-bars endpoint only

The symbol page continues to load bars via `GET /market-data/{symbol}/daily-bars` through the
typed `listDailyBars` client. Default limit 100 and max 500 remain unchanged. No backend
schema, route, or persistence changes are introduced in Phase 5.

### 2. Library: TradingView Lightweight Charts

The frontend depends on `lightweight-charts` for candlestick OHLC rendering plus a volume
histogram pane. The library owns mobile pan/zoom gestures. Chart construction runs in a Client
Component; the chart instance is disposed on unmount.

### 3. Table retention and accessibility

`DailyBarsTable` remains below the chart as the accessible, copyable tabular view. The chart
container exposes an accessible name of the form `{symbol} daily OHLC chart` (for example
`role="img"` with `aria-label`). Empty and error states stay non-crashing and operator-readable.

### 4. Presentation mapping only

API bars arrive newest-first. A pure adapter reverses them to chronological order and parses
string OHLC fields to numbers for the chart series. No derived indicators, scores, signals, or
order chrome are computed or displayed.

## Consequences

- `/symbols/[symbol]` shows a daily OHLC chart above the existing table for authenticated
  operators.
- Frontend gate `check:no-domain-logic` continues to forbid scoring/recommendation/prediction/
  trading module and export names.
- Future indicator overlays or alternate chart libraries require a superseding ADR.

## Explicitly out of scope

- Backend API or schema changes
- Technical indicators, scoring, recommendations, signals
- Order placement or trading UI
- NAS deployment
- Auth model changes (Phase 4 remains the session contract)

## Related documents

- [../overview.md](../overview.md)
- [0004-phase-3-operator-console.md](0004-phase-3-operator-console.md)
- [0005-phase-4-operator-auth.md](0005-phase-4-operator-auth.md)
