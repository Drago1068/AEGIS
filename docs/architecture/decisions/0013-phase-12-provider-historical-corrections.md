# ADR-0013: Phase 12 Provider Historical Corrections (Append-Only)

- Status: Accepted
- Date: 2026-07-29

## Context

ADR-0002 made re-ingestion idempotent via `ON CONFLICT DO NOTHING` on
`(source, symbol, event_time)`. That preserves point-in-time integrity for duplicate runs but
cannot represent provider-side revisions: when a vendor corrects a historical daily bar, AEGIS
must record a new observation rather than silently skip or overwrite the prior row.

Phases 10–11 added multiple sources and multi-source coverage weighting. Corrections remain
per `source`; each vendor revision is a new row with provenance, not a blended or merged bar.

## Decisions

### 1. Append-only correction rows

When re-ingest returns a bar for an existing `(source, symbol, event_time)` with a **material**
OHLCV or `data_quality` change, insert a **new row** with:

- `observation_kind = correction`
- `supersedes_observation_id` pointing to the prior current row's `id`
- later `ingested_at` (server default)

Prior rows are never updated or deleted.

### 2. Material change detection

Domain function `bars_materially_differ` compares stored snapshot vs incoming `DailyBar`:

- Prices (open/high/low/close): relative difference `> AEGIS_MARKET_DATA_CORRECTION_PRICE_EPSILON`
  (default `1e-6`)
- Volume: exact integer inequality
- `data_quality`: any string change is material (incoming bars are validated as primary today)

Identical re-ingest produces **no new row** (counted as skipped existing).

### 3. Schema

Drop unique constraint `uq_market_daily_bar_source_symbol_event_time` so multiple rows may share
`(source, symbol, event_time)`. Add:

| Column | Role |
| --- | --- |
| `observation_kind` | `initial` (default) or `correction` |
| `supersedes_observation_id` | Nullable FK to prior row `id` |

Existing rows are backfilled as `initial`. Primary key remains `(id, event_time)` for
TimescaleDB hypertable rules.

### 4. Read policy: current bars

`MarketDailyBarRepository.list_recent` and research bar loads return **current** observations:
for each `(source, symbol, trading_date)`, the row with the latest `ingested_at` wins.

No API history endpoint in Phase 12 MVP.

### 5. Ingestion orchestration

`MarketDataIngestionService`:

1. Load current snapshots for fetched trading dates.
2. New date → validate → insert `initial`.
3. Existing date, not material → skip.
4. Existing date, material → validate → insert `correction` with `supersedes_observation_id`.
5. Log structured `market_data_correction_applied` on correction insert.

`SymbolIngestionResult` adds `corrected_count` (initial inserts remain in `stored_count`).

### 6. Research and charts

No new research method. Assessments and charts read current bars via the repository; corrected
closes appear on the next on-demand or scheduled assessment run.

## Consequences

- Observation table may grow when vendors revise history; daily EOD revisions are expected to
  be rare.
- Point-in-time audits can compare initial vs correction rows via `supersedes_observation_id`.
- Calibration, actionable promotion, and blended multi-source bars remain out of scope.

## Explicitly out of scope

- Probability calibration / non-null `probability_confidence`
- Actionable promotion, recommendations, orders
- Blended / consensus OHLCV across sources
- Automatic full-history correction backfill jobs
- Intraday data, third provider, OAuth/MFA
- Chart UI for correction history
- UPDATE-in-place on observation rows

## Related documents

- [0002-phase-1-market-data-ingestion.md](0002-phase-1-market-data-ingestion.md)
- [../data-model.md](../data-model.md)
- [0011-phase-10-second-market-data-provider.md](0011-phase-10-second-market-data-provider.md)
