# Local Development

This is the day-to-day workflow for developing AEGIS 3.0 locally. See
[../architecture/overview.md](../architecture/overview.md) for module boundaries and
[configuration.md](configuration.md) for every environment variable.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (manages the backend Python interpreter and dependencies;
  no separate Python install is required).
- Node.js with Corepack enabled, matching [`frontend/.node-version`](../../frontend/.node-version)
  (Corepack provisions the exact pinned `pnpm` version from `packageManager` in
  [`frontend/package.json`](../../frontend/package.json)).
- Docker and Docker Compose v2 (for the full local stack and container-based checks).

## First-time setup

```sh
cp .env.example .env
```

`.env` is gitignored. Edit it only if you need non-default local ports or credentials; the
committed defaults work for `docker compose up` out of the box.

## Backend (`backend/`)

```sh
cd backend
uv sync --all-groups          # install dependencies + dev tools into backend/.venv
uv run uvicorn aegis.api.main:app --reload   # run the API locally (needs Postgres+Redis; see below)
uv run pytest                 # unit tests (incl. health/ready contract, no-domain-logic check)
uv run ruff check .           # lint
uv run pyright                # strict type-check
uv run alembic upgrade head   # apply migrations (requires AEGIS_DATABASE_URL to be reachable)
```

Running the API outside Docker requires a reachable PostgreSQL/TimescaleDB and Redis; the
simplest way to get both is `docker compose up -d postgres redis` (see below) while running
`uvicorn` on the host.

## Frontend (`frontend/`)

```sh
cd frontend
pnpm install                  # install dependencies (uses the pinned pnpm via Corepack)
pnpm dev                      # run the Next.js dev server
pnpm test                     # Vitest unit tests
pnpm lint                     # ESLint
pnpm exec tsc --noEmit        # strict type-check
pnpm run check:no-domain-logic
pnpm build                    # production build
```

## Full stack (Docker Compose)

```sh
docker compose config         # validate the compose file (no containers started)
docker compose up -d          # build and start postgres, redis, backend, frontend
docker compose ps             # confirm all four services report "healthy"
docker compose logs -f backend
docker compose down           # stop and remove containers (add -v to also drop volumes)
```

Once every service reports `healthy`:

- Backend liveness: `curl http://localhost:8000/health`
- Backend readiness: `curl http://localhost:8000/ready`
- Frontend: <http://localhost:3000>

## Cross-service integration tests (`tests/integration/`)

These require the full Compose stack to already be up and healthy (see
[../architecture/decisions/0001-phase-0-tooling.md](../architecture/decisions/0001-phase-0-tooling.md),
decision 6) and, for the market data and watchlist repository tests, migrations applied
(`uv run alembic upgrade head` from `backend/`). They reuse the backend's `uv`-managed
environment rather than a separate toolchain:

```sh
docker compose up -d
uv run --project backend pytest tests/integration -v
docker compose down
```

## Reproducible command reference

| Purpose | Command |
| --- | --- |
| Backend dev dependency sync | `uv sync --all-groups` (run from `backend/`) |
| Backend CI dependency sync | `uv sync --locked --all-groups` (run from `backend/`) |
| Backend execution (any tool) | `uv run ...` (run from `backend/`), e.g. `uv run pytest`, `uv run ruff check .`, `uv run pyright` |
| Frontend CI install | `pnpm install --frozen-lockfile` (run from `frontend/`) |
| Frontend dev install | `pnpm install` (run from `frontend/`) |
| Backend production image install | `uv sync --locked --no-dev --no-editable` (used inside `docker/backend.Dockerfile`) |
| Frontend production image install | `pnpm install --frozen-lockfile` + `pnpm build` (used inside `docker/frontend.Dockerfile`) |
| Cross-service integration tests | `uv run --project backend pytest tests/integration` (run from the repo root) |

See [ci.md](ci.md) for how these same commands are wired into `.github/workflows/ci.yml`, and
[security-scanning.md](security-scanning.md) for how to run the Phase 0 security checks
locally.
