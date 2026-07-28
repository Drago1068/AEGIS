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

## Backend: Phase 1 market data ingestion (`aegis.config.settings.Settings`)

| Variable | Description | Development default |
| --- | --- | --- |
| `AEGIS_ALPHA_VANTAGE_API_KEY` | Alpha Vantage API key. Optional at startup; ingestion returns a typed error if unset when invoked. Never logged. | unset |
| `AEGIS_ALPHA_VANTAGE_BASE_URL` | Base URL for the Alpha Vantage REST API. | `https://www.alphavantage.co/query` |
| `AEGIS_ALPHA_VANTAGE_REQUEST_INTERVAL_SECONDS` | Minimum delay between successive Alpha Vantage requests within one ingestion run, to stay within the provider's rate limit. | `12.0` |
| `AEGIS_WATCHLIST_SYMBOLS` | Comma-separated instrument symbols ingested by `POST /market-data/ingest`. Not a database table in Phase 1; see [ADR-0002](../architecture/decisions/0002-phase-1-market-data-ingestion.md). | `AAPL,MSFT,SPY` |
| `AEGIS_DAILY_BAR_OUTPUT_SIZE` | Alpha Vantage `outputsize` parameter: `compact` (latest ~100 daily bars) or `full` (full history). | `compact` |
| `AEGIS_EXCHANGE_CALENDAR_NAME` | `pandas-market-calendars` calendar name used to validate that a bar's trading date is a real exchange session day. | `NYSE` |
| `AEGIS_MAX_LATEST_BAR_STALENESS_TRADING_DAYS` | Maximum number of exchange trading days the most recent bar in a provider response may lag behind the current trading day before it is treated as stale. | `3` |

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
| `NEXT_PUBLIC_API_BASE_URL` | Base URL the frontend uses to reach the backend API. Exposed to the browser (`NEXT_PUBLIC_` prefix), so it must never carry a secret. | `http://localhost:8000` |
| `FRONTEND_PORT` | Host-side port mapping for the frontend container. | `3000` |

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
- `AEGIS_DATABASE_URL`, `AEGIS_REDIS_URL`, `AEGIS_ALPHA_VANTAGE_API_KEY` (and any future
  secret-bearing variable) must never appear in logs or in API error responses; see the
  `/ready` contract in [../architecture/overview.md](../architecture/overview.md), which
  reports dependency status without echoing connection strings, and the provider adapter in
  `aegis.providers.alpha_vantage`, which never logs the API key or the full request URL with
  the key attached.
