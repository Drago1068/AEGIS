# Configuration Reference

All AEGIS configuration is sourced from environment variables. Local development copies
[.env.example](../../.env.example) to a gitignored `.env` file. No file in this repository
contains a real secret, hostname, or credential; every value below is a documented,
non-functional development placeholder.

## Shared

| Variable | Used by | Description | Development default |
| --- | --- | --- | --- |
| `AEGIS_ENVIRONMENT` | backend | One of `development`, `test`, `ci`, `production`. | `development` |

## Backend (`aegis.config.settings.Settings`)

| Variable | Description | Development default |
| --- | --- | --- |
| `AEGIS_DATABASE_URL` | SQLAlchemy async connection string for PostgreSQL/TimescaleDB. | `postgresql+asyncpg://aegis:aegis@localhost:5432/aegis` |
| `AEGIS_REDIS_URL` | Connection string for Redis. | `redis://localhost:6379/0` |
| `AEGIS_READINESS_TIMEOUT_SECONDS` | Max time to wait for a single dependency check in `/ready`. | `2.0` |
| `AEGIS_API_HOST` | Host the FastAPI/uvicorn process binds to. | `0.0.0.0` |
| `AEGIS_API_PORT` | Port the FastAPI/uvicorn process binds to. | `8000` |
| `AEGIS_CORS_ORIGINS` | Comma-separated browser origins allowed by CORS (Phase 3 operator console). See [ADR-0004](../architecture/decisions/0004-phase-3-operator-console.md). | `http://localhost:3000` |

## Backend: Phase 1 / Phase 10 market data ingestion (`aegis.config.settings.Settings`)

| Variable | Description | Development default |
| --- | --- | --- |
| `AEGIS_DAILY_BAR_PRIMARY_SOURCE` | Primary daily-bar provider source id: `alpha_vantage` or `polygon`. See [ADR-0011](../architecture/decisions/0011-phase-10-second-market-data-provider.md). | `alpha_vantage` |
| `AEGIS_DAILY_BAR_SECONDARY_SOURCE` | Optional secondary source for failover on rate-limit / unavailable errors. Empty/unset disables failover. Must differ from primary when set. | unset |
| `AEGIS_ALPHA_VANTAGE_API_KEY` | Alpha Vantage API key. Optional at startup; ingestion returns a typed error if unset when that provider is invoked. Never logged. | unset |
| `AEGIS_ALPHA_VANTAGE_BASE_URL` | Base URL for the Alpha Vantage REST API. | `https://www.alphavantage.co/query` |
| `AEGIS_ALPHA_VANTAGE_REQUEST_INTERVAL_SECONDS` | Minimum delay between successive Alpha Vantage requests within one ingestion run, to stay within the provider's rate limit. | `12.0` |
| `AEGIS_POLYGON_API_KEY` | Polygon.io API key. Optional at startup; fails closed when that provider is invoked without a key. Never logged. | unset |
| `AEGIS_POLYGON_BASE_URL` | Base URL for the Polygon.io REST API (no trailing path). | `https://api.polygon.io` |
| `AEGIS_POLYGON_REQUEST_INTERVAL_SECONDS` | Configured pacing hint between Polygon requests within one ingestion run. | `12.0` |
| `AEGIS_WATCHLIST_SYMBOLS` | Comma-separated **bootstrap seed** symbols. As of Phase 2, only used to seed the database-backed `watchlist_symbols` table the first time it is empty; the database is the source of truth afterward. See [ADR-0003](../architecture/decisions/0003-phase-2-scheduled-watchlist.md). | `AAPL,MSFT,SPY` |
| `AEGIS_DAILY_BAR_OUTPUT_SIZE` | Lookback hint: Alpha Vantage `outputsize` (`compact` / `full`); Polygon calendar-day windows per ADR-0011. | `compact` |
| `AEGIS_EXCHANGE_CALENDAR_NAME` | `pandas-market-calendars` calendar name used to validate that a bar's trading date is a real exchange session day. | `NYSE` |
| `AEGIS_MAX_LATEST_BAR_STALENESS_TRADING_DAYS` | Maximum number of exchange trading days the most recent bar in a provider response may lag behind the current trading day before it is treated as stale. | `3` |
| `AEGIS_MARKET_DATA_CORRECTION_PRICE_EPSILON` | Relative OHLC tolerance for provider revision detection (ADR-0013). Incoming bars differing beyond this epsilon from the current stored bar trigger a correction row. | `0.000001` (`1e-6`) |

## Backend: Phase 2 scheduled ingestion & watchlist (`aegis.config.settings.Settings`)

| Variable | Description | Development default |
| --- | --- | --- |
| `AEGIS_INGESTION_SCHEDULE_ENABLED` | Whether the in-process APScheduler runs ingestion automatically. `false` leaves `POST /market-data/ingest` as the only trigger, matching Phase 1 behavior. | `true` |
| `AEGIS_INGESTION_CRON` | Standard 5-field cron expression (minute hour day month day-of-week, UTC) for the scheduled ingestion job. | `0 22 * * 1-5` |
| `AEGIS_INGESTION_SCHEDULE_LOCK_KEY` | Redis key used to ensure only one process runs a scheduled cycle at a time. | `aegis:ingestion:scheduler:lock` |
| `AEGIS_INGESTION_SCHEDULE_LOCK_TTL_SECONDS` | Redis lock TTL for a scheduled cycle; bounds how long a crashed process can hold the lock. Must cover ingest plus optional post-ingest research when enabled. | `1800` |

## Backend: Phase 8 post-ingest research (`aegis.config.settings.Settings`)

| Variable | Description | Development default |
| --- | --- | --- |
| `AEGIS_RESEARCH_SCHEDULE_AFTER_INGEST_ENABLED` | When `true`, after each successful locked scheduled ingest and after each successful on-demand `POST /market-data/ingest`, run Phase 6 `daily_bar_research_v1` for active watchlist symbols (stored bars only; fail-closed skips persist nothing). When `false`, Phase 6 on-demand `POST /research/{symbol}/assessments` is unchanged. Local and NAS example default `true`. See [ADR-0009](../architecture/decisions/0009-phase-8-scheduled-research.md). | `true` |
| `AEGIS_RESEARCH_OUTCOME_LABEL_AFTER_ASSESSMENT_ENABLED` | When `true`, after each successful research assessment from post-ingest research (when enabled) or on-demand `POST /research/{symbol}/assessments`, attempt Phase 13 `forward_total_return_v1` outcome labels (stored bars only; fail-closed skips log and persist nothing). When `false`, Phase 13 on-demand `POST .../outcome-labels` is unchanged. Local and NAS example default `true`. See [ADR-0015](../architecture/decisions/0015-phase-14-scheduled-outcome-labels.md). | `true` |
| `AEGIS_RESEARCH_CALIBRATION_AFTER_LABEL_ENABLED` | When `true`, after successful assessments (and after successful outcome labeling when that path runs), attempt Phase 15 `research_calibration_v1` using stored labeled historical corpus. Fail-closed skips log and persist nothing. When `false`, `probability_confidence` stays null unless prior calibration rows exist. Default `false`. See [ADR-0016](../architecture/decisions/0016-phase-15-research-probability-calibration.md). | `false` |
| `AEGIS_RESEARCH_CALIBRATION_MIN_CORPUS` | Minimum labeled historical assessments (excluding target) for `research_calibration_v1`. | `10` |
| `AEGIS_RESEARCH_CALIBRATION_MIN_BUCKET` | Minimum labeled examples in the research_index similarity bucket. | `5` |
| `AEGIS_RESEARCH_CALIBRATION_INDEX_BUCKET_WIDTH` | Absolute research_index tolerance for the similarity bucket. | `0.15` |

## Backend: Phase 11 multi-source coverage weighting (`aegis.config.settings.Settings`)

Research-only. Does not blend OHLCV or set `probability_confidence`. See
[ADR-0012](../architecture/decisions/0012-phase-11-multi-source-coverage-weighting.md).

| Variable | Description | Development default |
| --- | --- | --- |
| `AEGIS_RESEARCH_MULTI_SOURCE_COVERAGE_ENABLED` | When `true`, assessments use `method_version` 2 with source availability/agreement factors and preferred-source component series. When `false`, preserve Phase 6 `method_version` 1. | `true` |
| `AEGIS_RESEARCH_MULTI_SOURCE_CLOSE_TOLERANCE` | Relative close tolerance for agreement: `(max-min)/max` of usable closes on a comparable date. | `0.002` |
| `AEGIS_RESEARCH_MULTI_SOURCE_DISAGREEMENT_FAIL_CLOSED` | When `true`, fail closed if agreement factor is below the documented floor (`0.80`) when comparable dates exist. When `false`, only the soft product penalty applies. | `false` |
| `AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL` | When `false`, component series require 20 usable primary-quality bars from `AEGIS_DAILY_BAR_PRIMARY_SOURCE` only. When `true`, missing dates may be filled from the secondary source (no OHLCV blend). | `false` |

## Backend: Phase 4 operator authentication (`aegis.config.settings.Settings`)

| Variable | Description | Development default |
| --- | --- | --- |
| `AEGIS_OPERATOR_USERNAME` | Bootstrap operator username; seeds `operators` only when the table is empty. See [ADR-0005](../architecture/decisions/0005-phase-4-operator-auth.md). | `operator` |
| `AEGIS_OPERATOR_PASSWORD` | Bootstrap operator password (hashed at seed time; never logged). Change before non-local use. | `change-me-before-non-local-use` |
| `AEGIS_SESSION_COOKIE_NAME` | httpOnly session cookie name. | `aegis_session` |
| `AEGIS_SESSION_TTL_SECONDS` | Redis TTL and cookie max-age for a session. | `86400` |
| `AEGIS_SESSION_COOKIE_SECURE` | Mark the session cookie Secure (require HTTPS). | `false` |

On NAS with the optional Phase 9 TLS profile, keep this `true` and publish only `https://`
browser/API origins. Secure cookies are not sent over plain HTTP — a Secure+HTTP mismatch
fails closed in packaging validation when TLS is enabled. Local development stays
`false` with HTTP. See [ADR-0010](../architecture/decisions/0010-phase-9-nas-tls-reverse-proxy.md).

## PostgreSQL / TimescaleDB container (`docker-compose.yml`)

| Variable | Description | Development default |
| --- | --- | --- |
| `POSTGRES_USER` | Database role created by the official image entrypoint. | `aegis` |
| `POSTGRES_PASSWORD` | Password for `POSTGRES_USER`. Development-only placeholder; never reused in any real environment. | `aegis` |
| `POSTGRES_DB` | Database name created on first boot. | `aegis` |
| `POSTGRES_PORT` | Host-side port mapping for Postgres. | `5432` |

## Redis container (`docker-compose.yml`)

| Variable | Description | Development default |
| --- | --- | --- |
| `REDIS_PORT` | Host-side port mapping for Redis. | `6379` |

## Frontend (Next.js)

| Variable | Description | Development default |
| --- | --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | Base URL the frontend uses to reach the backend API. Exposed to the browser (`NEXT_PUBLIC_` prefix), so it must never carry a secret. For Docker image builds this value is passed as a build arg and inlined at `pnpm build` time (required for NAS packaging). | `http://localhost:8000` |
| `FRONTEND_PORT` | Host-side port mapping for the frontend container. | `3000` |

## NAS deployment (Phase 7 + optional Phase 9 TLS)

NAS-specific variables live in gitignored `.env.nas` (template: [`.env.nas.example`](../../.env.nas.example)).
They are not read by application Settings directly beyond the usual `AEGIS_*` / Compose vars;
deploy/verify scripts also require connection and public-URL settings.

| Variable | Used by | Description | Example placeholder |
| --- | --- | --- | --- |
| `AEGIS_NAS_SSH_HOST` | deploy/verify scripts | SSH hostname or address of the NAS. Never commit a real value. | `replace-with-nas-ssh-hostname-or-ip` |
| `AEGIS_NAS_SSH_USER` | deploy/verify scripts | SSH username. | `replace-with-nas-ssh-username` |
| `AEGIS_NAS_SSH_PORT` | deploy/verify scripts | SSH port. | `22` |
| `AEGIS_NAS_SSH_IDENTITY_FILE` | deploy/verify scripts | Optional path to an SSH private key. | unset |
| `AEGIS_NAS_REMOTE_DIR` | deploy/verify scripts | Absolute remote directory for the unpacked package. | `replace-with-absolute-remote-deploy-directory` |
| `AEGIS_NAS_COMPOSE_PROJECT_NAME` | Compose overlay | Compose project name on the NAS. | `aegis` |
| `AEGIS_NAS_API_BASE_URL` | verify scripts | Operator-facing API origin used for HTTP(S) checks. | `https://replace-with-operator-facing-api-origin` |
| `AEGIS_NAS_FRONTEND_BASE_URL` | verify scripts | Operator-facing frontend origin. | `https://replace-with-operator-facing-frontend-origin` |
| `AEGIS_NAS_TLS_ENABLED` | package/deploy/validate/verify | When `true`, include `docker-compose.nas.tls.yml` (Caddy). | `false` |
| `AEGIS_TLS_MODE` | TLS scripts / Caddyfile choice | `files` (operator PEMs) or `acme` (public DNS). | `files` |
| `AEGIS_TLS_FRONTEND_HOST` | Caddy | Console hostname (no scheme). Required when TLS enabled. | `replace-with-frontend-hostname` |
| `AEGIS_TLS_API_HOST` | Caddy | API hostname (no scheme). Required when TLS enabled. | `replace-with-api-hostname` |
| `AEGIS_TLS_HTTPS_PORT` | TLS Compose | Host port published for HTTPS. | `443` |
| `AEGIS_TLS_HTTP_PORT` | TLS Compose | Host port for HTTP→HTTPS redirect. | `80` |
| `AEGIS_TLS_CADDYFILE` | TLS Compose | Caddyfile path relative to `docker/nas/`. | `./proxy/Caddyfile.files` |
| `AEGIS_TLS_CERTS_DIR` | TLS Compose / deploy | Host directory of PEMs (files mode). | `./proxy/certs` |
| `AEGIS_TLS_ACME_EMAIL` | Caddy ACME | Contact email for certificate issuance (`acme` mode). | `replace-with-operator-acme-contact-email` |
| `AEGIS_NAS_VERIFY_CURL_INSECURE` | verify scripts | Lab-only: pass `curl -k` for self-signed certs. | `false` |

On NAS, set a **non-default** `AEGIS_OPERATOR_PASSWORD` and prefer
`AEGIS_SESSION_COOKIE_SECURE=true` when HTTPS terminates in front of the console. Align
`AEGIS_CORS_ORIGINS` and `NEXT_PUBLIC_API_BASE_URL` to the same `https://` origins. See
[nas-deployment.md](nas-deployment.md), [../../docker/nas/README.md](../../docker/nas/README.md),
and [ADR-0010](../architecture/decisions/0010-phase-9-nas-tls-reverse-proxy.md).

Caddy sets `X-Forwarded-For` / `X-Forwarded-Proto` / `X-Forwarded-Host` toward the backend
and frontend. Session `Secure` remains env-driven (`AEGIS_SESSION_COOKIE_SECURE`); the proxy
does not replace Phase 4 application auth.

## Testing (`tests/integration/`)

| Variable | Description | Development default |
| --- | --- | --- |
| `AEGIS_INTEGRATION_BACKEND_URL` | Base URL the cross-service integration tests use to reach a running backend container. Not read by application code. | `http://localhost:8000` |

## Rules

- Every new environment variable introduced by any future phase must be added to
  `.env.example` and to this document in the same change.
- No secret, token, credential, hostname, or private IP address may be hardcoded in source
  code, Dockerfiles, or committed configuration. Production values are supplied at deploy
  time via the runtime environment, never committed.
- `AEGIS_DATABASE_URL`, `AEGIS_REDIS_URL`, `AEGIS_ALPHA_VANTAGE_API_KEY`,
  `AEGIS_POLYGON_API_KEY` (and any future secret-bearing variable) must never appear in logs
  or in API error responses; see the `/ready` contract in
  [../architecture/overview.md](../architecture/overview.md), which reports dependency status
  without echoing connection strings, and the provider adapters in
  `aegis.providers.alpha_vantage` / `aegis.providers.polygon`, which never log API keys
  (Polygon uses Bearer auth so the key is not placed in query strings).
