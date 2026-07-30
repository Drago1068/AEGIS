# ADR-0056: Phase 55 Research Cross-Source Fill and Session-Depth Bar Load

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 54 live evidence showed Polygon failover can store ~500 daily bars after Alpha
Vantage rejects ``outputsize=full`` on free tiers. Assessment backfill still failed many
older as-of dates with ``insufficient_primary_bars`` from ``alpha_vantage`` because:

1. ``AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL`` defaulted to ``false`` (ADR-0012),
   so secondary sessions could not fill missing primary dates.
2. Research bar loads used ``list_recent(limit=N)``, which caps **observation rows**. With
   two sources on overlapping recent dates, dual rows exhaust ``N`` before older
   secondary-only sessions enter the window — so deep Polygon history never reaches
   ``assess_from_bars``.

## Decisions

### 1. Default cross-source component fill on

Default ``AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL`` to **``true``**. Operators may
still set ``false`` for primary-only labs. Filling still prefers primary on overlapping
dates and never blends OHLCV on a single date (ADR-0012 semantics unchanged).

### 2. Session-depth research loads

Research paths load bars via ``MarketDailyBarRepository.list_recent_for_sessions``:

- ``AEGIS_RESEARCH_BAR_LOAD_LIMIT`` means the most recent **N distinct trading dates**.
- All current source rows for those dates are returned (may exceed N rows).
- HTTP ``GET .../daily-bars`` keeps row-limited ``list_recent`` (operator browse UX).

### 3. Compose pass-through

Wire ``AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL`` into local and NAS Compose
backend environments (default ``true``).

### 4. Out of scope

- Changing coverage agreement floors or fail-closed disagreement
- Guaranteeing calibration readiness on every symbol
- Default-on calibration, actionable promotion, orders, ACME
- NAS live verify (follow-up ops phase)

## Related documents

- [0012-phase-11-multi-source-coverage-weighting.md](0012-phase-11-multi-source-coverage-weighting.md)
- [0054-phase-53-full-daily-bar-history.md](0054-phase-53-full-daily-bar-history.md)
- [0055-phase-54-nas-live-verify-phase-53.md](0055-phase-54-nas-live-verify-phase-53.md)
- [../../operations/configuration.md](../../operations/configuration.md)
