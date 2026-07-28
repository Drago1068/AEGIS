# ADR-0003: Phase 2 Scheduled Ingestion and Database-Backed Watchlist

- Status: Accepted
- Date: 2026-07-28

## Context

Phase 1 (ADR-0002) deferred two explicit limitations: ingestion only runs on-demand via
`POST /market-data/ingest`, and the watchlist is a static, comma-separated environment
variable (`AEGIS_WATCHLIST_SYMBOLS`), not something an operator can change without a redeploy.
Phase 2 turns both into real features: a background schedule that runs ingestion
automatically, and a database-backed watchlist that can be managed via the API while the
service is running. Several concrete choices were open and are recorded here.

## Decisions

### 1. Scheduler: in-process APScheduler (`AsyncIOScheduler`)

`apscheduler` (3.x, `AsyncIOScheduler`) runs inside the existing FastAPI process, started in
the application lifespan and stopped on shutdown. No separate worker process, message queue,
or external scheduler (Celery beat, system cron calling the API, Kubernetes CronJob) is
introduced.

Rationale: Compose runs a single backend replica; an in-process scheduler needs no new
infrastructure, container, or network path, and keeps the vertical slice minimal.
**Deferred**: if AEGIS ever runs multiple backend replicas or moves ingestion to a separate
worker, this decision should be revisited via a new ADR.

### 2. Coordination: a Redis lock, not "assume one process"

Because a second backend replica could theoretically start (for example during a rolling
deploy), the scheduled job always acquires a Redis lock (`SET key value NX EX <ttl>`) before
running and releases it (`DELETE`) when done; a process that cannot acquire the lock skips
that cycle instead of running a duplicate ingestion pass. The lock also self-expires via its
TTL (`AEGIS_INGESTION_SCHEDULE_LOCK_TTL_SECONDS`), so a crashed process cannot wedge the lock
forever. This logic lives in `aegis.domain.scheduled_ingestion.run_locked_ingestion_cycle`,
which depends only on `Protocol` interfaces (`DistributedLock`, `WatchlistSource`,
`IngestionRunner`) - never a concrete Redis client, database session, or scheduler library -
so it is unit-testable with fakes exactly like `MarketDataIngestionService` (ADR-0002). The
real Redis/database/APScheduler wiring lives in `aegis.api.scheduler`, mirroring how
`aegis.api.dependencies` wires the on-demand path.

### 3. Watchlist storage: a mutable, soft-deletable operational table

`watchlist_symbols` (plain Postgres table, not a TimescaleDB hypertable) stores
`id, symbol, is_active, created_at, updated_at`. Removing a symbol sets `is_active=false`
(`DELETE /watchlist/{symbol}`); rows are never hard-deleted, so re-adding a symbol reactivates
its existing row instead of creating a duplicate history.

This is deliberately **not** built to the append-only, point-in-time conventions in
[data-model.md](../data-model.md): a watchlist is current operational configuration ("which
symbols do we currently track"), not a market observation or evidence record, so those
conventions do not apply here. Both the on-demand endpoint and the scheduled job read the same
`list_active()` query, so they can never disagree about which symbols are current.

### 4. Bootstrap: environment variable seeds an empty table once, then the database wins

`AEGIS_WATCHLIST_SYMBOLS` (comma-separated, unchanged format) is now a **bootstrap seed**, not
the live watchlist. `WatchlistRepository.ensure_seeded()` inserts the seed symbols only if the
table is completely empty (zero rows, active or inactive), and is called on every watchlist
read (both the API dependency and the scheduled job), so it is safe to call repeatedly and
requires no separate startup migration step. Once any row exists, seeding never runs again -
an operator deactivating every symbol is a deliberate choice, not a signal to re-seed.

### 5. Watchlist API: backend only, no frontend

`GET /watchlist`, `POST /watchlist`, and `DELETE /watchlist/{symbol}` are the only interface
for Phase 2. The frontend remains untouched (still the Phase 0 placeholder page); a UI for
managing the watchlist is deferred to a later phase, once there is a concrete need for
non-technical operators to manage it without the API directly.

### 6. Symbol validation: a stricter shape check on API input than the seed parser

User-submitted symbols (`POST /watchlist`) are normalized and validated by
`aegis.domain.watchlist.normalize_symbol` (uppercase, 1-20 characters, must start with a
letter, remaining characters limited to `A-Z0-9.-`) before being persisted, rejecting shapes
that could never be a real ticker with a typed `422` (via a Pydantic `field_validator`, which
calls the same domain function). The environment-sourced seed list keeps the simpler
strip/uppercase/deduplicate parsing from Phase 1 (`Settings.watchlist_seed_symbols`), since it
is developer-controlled configuration, not untrusted HTTP input.

### 7. Authentication: still none (limitation reaffirmed, not revisited)

`POST/GET/DELETE /watchlist` and `POST /market-data/ingest` remain unauthenticated, per the
accepted limitation in ADR-0002. Scheduling ingestion automatically does not, by itself,
increase the urgency of adding authentication (the service is still local/trusted-network
only), but it does mean an unauthenticated `POST /watchlist` change now has an effect the very
next scheduled run rather than only on the next manual `POST /market-data/ingest` call. This
is noted as a slightly larger blast radius for the same accepted limitation, not a new one.

## Consequences

- `POST /market-data/ingest`'s `symbols` parameter now comes from
  `aegis.api.dependencies.get_active_watchlist_symbols` (DB-backed), replacing the Phase 1
  `get_watchlist_symbols` (env-backed) dependency, which is removed.
- `apscheduler` becomes a new main runtime dependency of the backend package.
- A new Alembic migration (`0003`) adds `watchlist_symbols` as a plain (non-hypertable) table.
- Disabling the schedule entirely (`AEGIS_INGESTION_SCHEDULE_ENABLED=false`) is fully
  supported and leaves the on-demand endpoint as the only ingestion trigger, matching Phase 1
  behavior exactly except for where the symbol list comes from.

## Explicitly out of scope

- Any scoring, probability, confidence, or recommendation computation.
- Any order placement/transmission code path.
- Frontend changes of any kind.
- Authentication/authorization on any endpoint.
- A second data provider, intraday granularity, or provider-side correction handling.
- A separate worker process, message queue, or multi-replica-aware scheduling beyond the
  Redis lock described above.

## Related documents

- [../overview.md](../overview.md)
- [../data-model.md](../data-model.md)
- [0002-phase-1-market-data-ingestion.md](0002-phase-1-market-data-ingestion.md)
