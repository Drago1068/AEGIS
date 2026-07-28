# ADR-0002: Phase 1 Market Data Ingestion Decisions

- Status: Accepted
- Date: 2026-07-27

## Context

Phase 0 established the repository, tooling, and infrastructure foundation with no domain
logic. Phase 1 introduces the first real external data integration: a typed provider adapter,
a validated append-only observation store, and an on-demand ingestion endpoint, per
`CLAUDE.md`'s "data ingestion / provider adapters" scope for this phase. Several concrete
choices were open and are recorded here so they are not re-litigated implicitly file-by-file.

## Decisions

### 1. Provider: Alpha Vantage `TIME_SERIES_DAILY`

Alpha Vantage's free-tier `TIME_SERIES_DAILY` endpoint is the first provider adapter. It
returns unadjusted daily open/high/low/close/volume bars in JSON. The adjusted-close endpoint
(`TIME_SERIES_DAILY_ADJUSTED`) is now premium-gated by Alpha Vantage and is out of scope.

Rationale: a simple REST/JSON API with a usable free tier, well suited to a first vertical
slice. Alternatives considered: Finnhub (real-time quotes, different free-tier shape), Twelve
Data, Polygon.io (end-of-day only on the free tier). Swapping or adding providers later requires
only a new adapter behind the existing `DailyBarProvider` protocol, not a domain-layer change.

### 2. Granularity: daily bars only

Phase 1 ingests and stores daily OHLCV bars exclusively. Real-time/intraday quotes are
explicitly deferred to a later phase; the closed-session/staleness validation rules in
`docs/architecture/market-data-contracts.md` are interpreted for daily-bar granularity (see
Decision 6).

### 3. Ingestion trigger: on-demand only

Ingestion runs only when `POST /market-data/ingest` is called. No background scheduler (cron,
APScheduler, Celery beat, etc.) exists in Phase 1. This keeps the vertical slice minimal and
avoids introducing a scheduling/coordination dependency before it is needed.

**Deferred**: scheduled/background ingestion is expected in a later phase once ingestion
reliability and provider rate limits have been exercised manually.

### 4. Watchlist: configuration, not a database table

The set of symbols ingested is a comma-separated environment variable
(`AEGIS_WATCHLIST_SYMBOLS`), read via `Settings`, not a database table. A user-manageable,
database-backed watchlist is deferred.

**Deferred**: a dynamic watchlist (with a frontend to manage it) is a later-phase feature once
there is a real use case for changing it without a redeploy.

### 5. Exchange calendar: `pandas-market-calendars`

`pandas-market-calendars` (MIT license) supplies exchange trading-day calendars. It is wrapped
behind `aegis.domain.calendars`, a thin function-based interface, so the concrete library
remains swappable and the calendar identity (`AEGIS_EXCHANGE_CALENDAR_NAME`, default `NYSE`) is
configuration rather than a hardcoded assumption, per the calendar requirement in
`docs/architecture/market-data-contracts.md`.

### 6. Validation rules adapted for daily-bar granularity

The five rejection categories in `docs/architecture/market-data-contracts.md`
(invalid/stale/non-positive/closed-session/otherwise-unusable) are implemented as follows for
daily bars:

- **Invalid**: malformed/missing OHLCV fields.
- **Non-positive**: zero or negative open/high/low/close/volume.
- **Closed-session**: the bar's `trading_date` is not a valid session day on the configured
  exchange calendar (catches provider errors, weekends, and holidays for daily granularity,
  where there is no intraday open/closed state to check).
- **Stale**: evaluated only against the most-recent bar returned in an ingestion run (compared
  to the exchange's most recent trading day, within `AEGIS_MAX_LATEST_BAR_STALENESS_DAYS`) to
  detect a stale provider response. It is never applied to older bars during a historical
  backfill, since an old `trading_date` there is expected, not a data-quality defect.
- **Otherwise unusable**: Alpha Vantage's "200 OK with an error body" responses (`Error
  Message` / `Note` / `Information` keys instead of the expected time-series structure) are
  detected in the provider adapter and raised as a typed `ProviderError`/
  `ProviderRateLimitError` before validation ever sees them, so a rate-limited or
  premium-gated response can never be mistaken for an empty-but-valid result.

### 7. No authentication on the ingestion endpoint (accepted limitation)

`POST /market-data/ingest` and `GET /market-data/{symbol}/daily-bars` have no authentication in
Phase 1. This is an explicit, documented limitation, not an oversight: the service is
self-hosted and intended for local/trusted-network access only in this phase, it never places
or transmits orders, and network exposure (including any NAS deployment) remains out of scope
until its own phase and evidence gate.

**Deferred**: authentication/authorization is required before this API is exposed beyond a
local/trusted network.

### 8. Idempotent inserts, not corrections

The `market_daily_bar_observations` table has a unique constraint on `(source, symbol,
trading_date)`. Re-running ingestion for a symbol/day already stored is a no-op skip
(`ON CONFLICT DO NOTHING`), not a duplicate row. This is distinct from the append-only
"correction" pattern in `docs/architecture/data-model.md`: a skip means "we already have this
fact," whereas a correction means "a new, later observation supersedes an old one." Phase 1 does
not implement provider-side correction handling; if a provider revises a historical daily bar,
that is deferred to a later phase.

## Consequences

- Adding a second provider or intraday granularity later means adding a new adapter/table
  alongside the existing ones, not restructuring `providers/`, `domain/`, or `persistence/`.
- The ingestion endpoint must not be exposed outside a trusted network until an auth phase is
  completed; this is an operational constraint to document at deployment time, not just here.
- `httpx` moves from a test-only dependency to a main runtime dependency of the backend package.

## Related documents

- [../overview.md](../overview.md)
- [../data-model.md](../data-model.md)
- [../market-data-contracts.md](../market-data-contracts.md)
- [0001-phase-0-tooling.md](0001-phase-0-tooling.md)
