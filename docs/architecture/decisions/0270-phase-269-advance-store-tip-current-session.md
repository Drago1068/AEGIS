# ADR-0270: Phase 269 Advance Store Tip When Provider Has Current Session

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 267–268 closed opaque mixed ``latest_resolved_label_bar_source`` (concrete
``polygon`` on live AAPL). Live verify still showed ``stored_bar_calendar_lag_trading_days=1``
with winning tip ``2026-07-30`` after the ``2026-07-31`` session (post-close lab time).

NAS diagnosis (lab TLS backend):

- Range aggregates ``/v2/aggs/.../range/1/day/...`` returned tip ``2026-07-30`` with
  ``status=DELAYED`` (30-day and full windows).
- ``/v1/open-close/AAPL/2026-07-31`` returned ``403`` (“today’s data before end of day”).
- ``/v2/aggs/ticker/AAPL/prev`` returned the settled ``2026-07-31`` close (real provider
  bar; not invented).

Prefer merging Polygon previous-close when it advances the tip over inventing closes or
adding more evidence scalars.

## Decisions

### 1. Polygon ``/prev`` tip catch-up

After a successful range fetch, ``PolygonProvider`` calls ``/v2/aggs/ticker/{ticker}/prev``
(unadjusted) and appends that bar when its trading date is absent from the range results.
Prev failures soft-skip so a healthy range response is retained. Validation / ingest still
reject unusable bars; no invented closes.

### 2. Out of scope

Inventing closes, Alpha Vantage tip invention, default-on calibration, orders.

### 3. Why this next

Label-bar provenance was clear; remaining operator gap was calendar lag while Polygon
already exposed the session via ``/prev``.

## Consequences

- Ingest can store the settled session when range aggregates lag.
- Phase 270 live-verifies tip / lag under lab TLS.

## Related documents

- [0269-phase-268-nas-live-verify-phase-267.md](0269-phase-268-nas-live-verify-phase-267.md)
- [0271-phase-270-nas-live-verify-phase-269.md](0271-phase-270-nas-live-verify-phase-269.md)
- [0262-phase-261-provider-tip-ahead-of-store.md](0262-phase-261-provider-tip-ahead-of-store.md)
- [0011-phase-10-second-market-data-provider.md](0011-phase-10-second-market-data-provider.md)
