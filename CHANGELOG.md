# Changelog

All notable changes to this project are documented in this file. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses phase-based
versioning until a first stable release (see [CLAUDE.md](CLAUDE.md) for the phase-gated
delivery workflow).

## [Unreleased]

### Phase 3 - Operator Console (Frontend)

A browser operator console for the existing Phase 1/2 APIs: manage the watchlist, trigger
on-demand ingest, and browse stored daily bars as a table. No scoring, recommendation,
prediction, chart libraries, authentication, or order-placement logic exists in this phase;
see
[docs/architecture/decisions/0004-phase-3-operator-console.md](docs/architecture/decisions/0004-phase-3-operator-console.md).

#### Added

- Frontend console (`frontend/`): `/` watchlist + ingest panels; `/symbols/[symbol]` daily-bar
  table; Source Sans 3 / IBM Plex Mono typography; typed API client extensions for watchlist,
  ingest, and daily bars; Vitest coverage for the client and key components.
- Backend CORS: `AEGIS_CORS_ORIGINS` setting and `CORSMiddleware` so the Next.js origin can call
  the API from the browser; Compose passes the setting through; unit tests cover allow-listed
  vs rejected preflight origins.

#### Explicitly out of scope

Authentication, chart libraries/indicators/scoring, schedule configuration UI, second
providers, corrections, and NAS deployment - each is absent, not merely unimplemented, per the
Phase 3 plan.

### Phase 2 - Scheduled Ingestion & Database-Backed Watchlist

Ingestion now runs automatically on a schedule, and the watchlist moves from a static
environment variable to a database-backed list manageable via the API while the service is
running. No scoring, recommendation, prediction, or order-placement logic exists anywhere in
this phase; see
[docs/architecture/decisions/0003-phase-2-scheduled-watchlist.md](docs/architecture/decisions/0003-phase-2-scheduled-watchlist.md)
for the confirmed decisions (scheduler, coordination lock, watchlist storage, bootstrap,
validation, auth) and their accepted limitations.

#### Added

- Domain layer (`backend/src/aegis/domain/`): `watchlist.py` (`normalize_symbol`, a
  framework-free shape validator for user-submitted symbols) and `scheduled_ingestion.py`
  (`run_locked_ingestion_cycle`, a framework-free, `Protocol`-based lock-guarded ingestion
  cycle - independently unit-tested with fake Redis/watchlist/ingestion-service doubles, no
  real I/O).
- Persistence (`backend/src/aegis/persistence/`): `WatchlistSymbol` model and
  `WatchlistRepository` (`list_active`, `list_active_rows`, `add`, `deactivate`,
  `ensure_seeded`), plus an Alembic migration (`0003`) creating `watchlist_symbols` as a plain
  (non-hypertable) table with a unique constraint on `symbol`. Unlike
  `market_daily_bar_observations`, this table is a mutable, soft-deletable operational list,
  not an append-only observation (see ADR-0003).
- API (`backend/src/aegis/api/`): `GET /watchlist`, `POST /watchlist`, and
  `DELETE /watchlist/{symbol}` for watchlist management; `POST /market-data/ingest` now reads
  the active database-backed watchlist instead of `AEGIS_WATCHLIST_SYMBOLS` directly.
  `scheduler.py` wires an APScheduler `AsyncIOScheduler` into the application lifespan, running
  `run_locked_ingestion_cycle` on a cron schedule (`AEGIS_INGESTION_CRON`) guarded by a Redis
  lock (`AEGIS_INGESTION_SCHEDULE_LOCK_KEY`/`_TTL_SECONDS`) so multiple backend replicas can
  never run overlapping cycles; disabled entirely via `AEGIS_INGESTION_SCHEDULE_ENABLED=false`.
- Configuration: `AEGIS_INGESTION_SCHEDULE_ENABLED`, `AEGIS_INGESTION_CRON`,
  `AEGIS_INGESTION_SCHEDULE_LOCK_KEY`, `AEGIS_INGESTION_SCHEDULE_LOCK_TTL_SECONDS`, documented
  in `.env.example` and `docs/operations/configuration.md`. `AEGIS_WATCHLIST_SYMBOLS`'s role
  changes from "the watchlist" to "the one-time bootstrap seed" for the database table.
- Unit tests for symbol validation, the locked scheduled-ingestion cycle (fake doubles, no real
  I/O), the watchlist endpoints (dependency overrides), and scheduler lifespan wiring
  (enabled/disabled); a new cross-service integration test
  (`tests/integration/test_watchlist_repository_docker.py`) verifying the migration and the
  repository's add/deactivate/reactivate/seed behavior against the real Compose Postgres
  service.
- `apscheduler` added as a new main runtime dependency.

#### Explicitly out of scope

Any scoring/probability/confidence/recommendation computation, order placement/transmission,
frontend changes, authentication on any endpoint, a second data provider or intraday
granularity, and a separate worker process or multi-replica-aware scheduling beyond the Redis
lock - each is absent, not merely unimplemented, per the Phase 2 plan.

### Phase 1 - Market Data Ingestion (Alpha Vantage daily bars)

The first real external data integration: a typed Alpha Vantage provider adapter, validated
daily-bar rejection rules, an append-only TimescaleDB observation store, and on-demand
ingest/read API endpoints. No scoring, recommendation, prediction, or order-placement logic
exists anywhere in this phase; see
[docs/architecture/decisions/0002-phase-1-market-data-ingestion.md](docs/architecture/decisions/0002-phase-1-market-data-ingestion.md)
for the confirmed decisions (provider, granularity, trigger, watchlist, calendar, auth,
idempotency) and their accepted limitations.

#### Added

- Provider adapter (`backend/src/aegis/providers/`): `DailyBarProvider` protocol,
  `AlphaVantageProvider` (Alpha Vantage `TIME_SERIES_DAILY`, unadjusted daily OHLCV), and typed
  `ProviderError`/`ProviderRateLimitError` for both HTTP failures and Alpha Vantage's
  "200 OK with an error body" responses (invalid symbol, rate limit, premium-tier gate).
- Domain layer (`backend/src/aegis/domain/`): a swappable exchange-calendar wrapper
  (`calendars.py`, backed by `pandas-market-calendars`); daily-bar validation
  (`market_data_validation.py`) implementing every rejection rule from
  `docs/architecture/market-data-contracts.md` (invalid OHLC shape, non-positive values,
  closed-session/non-trading-day, and latest-bar staleness); and `MarketDataIngestionService`
  (`market_data_ingestion.py`) orchestrating fetch, validate, and idempotent persistence per
  watchlist symbol, isolating one symbol's provider failure from the rest of the run.
- Persistence (`backend/src/aegis/persistence/`): `MarketDailyBarObservation` model and
  `MarketDailyBarRepository`, plus an Alembic migration creating
  `market_daily_bar_observations` as a TimescaleDB hypertable (partitioned on `event_time`)
  with a unique constraint on `(source, symbol, event_time)` for idempotent re-ingestion.
- API (`backend/src/aegis/api/`): `POST /market-data/ingest` (runs one ingestion cycle over the
  configured watchlist) and `GET /market-data/{symbol}/daily-bars` (reads stored bars, 404 for
  an unknown symbol). No authentication in Phase 1 (self-hosted, local/trusted-network only;
  see ADR-0002).
- Configuration: `AEGIS_ALPHA_VANTAGE_API_KEY`, `AEGIS_ALPHA_VANTAGE_BASE_URL`,
  `AEGIS_ALPHA_VANTAGE_REQUEST_INTERVAL_SECONDS`, `AEGIS_WATCHLIST_SYMBOLS`,
  `AEGIS_DAILY_BAR_OUTPUT_SIZE`, `AEGIS_EXCHANGE_CALENDAR_NAME`, and
  `AEGIS_MAX_LATEST_BAR_STALENESS_TRADING_DAYS`, documented in `.env.example` and
  `docs/operations/configuration.md`.
- Unit tests for the provider adapter (`httpx.MockTransport`), calendar wrapper, validation
  rules, ingestion orchestration (fake provider/repository doubles, no real I/O), and both API
  endpoints (dependency overrides); a new cross-service integration test
  (`tests/integration/test_market_data_repository_docker.py`) verifying the migration,
  hypertable, and idempotent insert/read round trip against the real Compose Postgres/
  TimescaleDB service.
- `httpx` promoted from a test-only to a main runtime dependency; `pandas-market-calendars`
  added as a new main runtime dependency.

#### Explicitly out of scope

Order placement/transmission, any scoring/probability/confidence/recommendation computation,
background/scheduled ingestion, authentication on the new endpoints, a database-backed
watchlist, and any frontend change - each is absent, not merely unimplemented, per the Phase 1
plan.

### Phase 0 - Architecture & Repository Foundation

Repository and architecture foundation. No scoring, recommendation, prediction, or order-
placement logic exists anywhere in this phase; see
[docs/architecture/decisions/0001-phase-0-tooling.md](docs/architecture/decisions/0001-phase-0-tooling.md)
for the tooling decisions and
[docs/operations/](docs/operations/) for operational documentation.

#### Added

- Architecture documentation: system overview, data-model conventions (append-only,
  versioned, provenance-aware observations; coverage vs. probability confidence;
  research-only vs. actionable state), and market-data quote-rejection contracts.
- Backend service (`backend/`): FastAPI application on Python 3.12 managed with `uv`, exposing
  `/health` (liveness) and `/ready` (readiness against PostgreSQL/TimescaleDB and Redis), a
  baseline Alembic migration enabling the TimescaleDB extension, unit tests, and a scoped
  no-domain-logic structural check.
- Frontend service (`frontend/`): Next.js + TypeScript + Tailwind CSS application managed with
  pnpm, a single placeholder page, a typed API client for the backend health contract, and an
  equivalent no-domain-logic check.
- Local Docker Compose topology (`docker-compose.yml`) with health-checked `postgres`, `redis`,
  `backend`, and `frontend` services, plus pinned, non-root Dockerfiles for the backend and
  frontend and a build-only `linux/amd64` validation step for the UGREEN NAS target
  architecture (`docker/nas/README.md` documents the deployment boundary; no deployment occurs).
- Cross-service integration test (`tests/integration/`) verifying the readiness endpoint against
  the real Compose stack.
- CI workflow (`.github/workflows/ci.yml`) with backend, frontend, compose-validation,
  integration, and security-scanning jobs, and documentation of which gates are local-only vs.
  remote-dependent (`docs/operations/ci.md`).
- Security scanning documentation and local commands for dependency (`pip-audit`, `pnpm audit`),
  secret (`gitleaks`), and container-image (`trivy`) scans (`docs/operations/security-scanning.md`).
- Environment configuration reference (`.env.example`, `docs/operations/configuration.md`) and
  day-to-day developer workflow documentation (`docs/operations/local-development.md`).
- `.gitleaks.toml` allowlisting vendored/build directories for local secret scanning.

#### Fixed

- Backend: bumped `pytest`/`pytest-asyncio` to remediate a `pytest` CVE
  (`PYSEC-2026-1845`).
- Frontend: pinned `sharp` and `postcss` to patched versions via `pnpm-workspace.yaml`
  `overrides` (both are transitive `next` dependencies, not direct dependencies) to remediate
  `GHSA-f88m-g3jw-g9cj`, `GHSA-6g55-p6wh-862q`, `GHSA-r28c-9q8g-f849`, and
  `GHSA-qx2v-qp2m-jg93`.
- Docker images: both Dockerfiles now run `apt-get upgrade` in the final stage to pick up
  Debian security patches published after the pinned base image tag; the frontend image also
  removes the unused, bundled `npm`/`npx` CLI (this image only ever runs `node server.js`),
  eliminating scanner findings for code that is never executed. Both images scan clean at
  `trivy image --severity HIGH,CRITICAL --ignore-unfixed` as of this entry.
