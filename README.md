# AEGIS 3.0

AEGIS 3.0 is a greenfield, self-hosted market decision-support platform. It is decision-support
software only: it never places or transmits live orders (see [CLAUDE.md](CLAUDE.md) and
[.cursor/rules/aegis-project.mdc](.cursor/rules/aegis-project.mdc) for the full project rules).

Development starts locally in this repository. Deployment to the UGREEN NAS is performed only
after the current phase passes its documented local acceptance gate.

**Current phase: Phase 25 (NAS live verify of Phase 24).** Redeploy and evidence gate for
`GET /research/{symbol}/evidence-summary/export` (ADR-0026). See
[docs/architecture/decisions/0026-phase-25-nas-live-verify-phase-24.md](docs/architecture/decisions/0026-phase-25-nas-live-verify-phase-24.md)
and [CHANGELOG.md](CHANGELOG.md).

## Quick start

```sh
cp .env.example .env

cd backend && uv sync --all-groups && cd ..
cd frontend && pnpm install && cd ..

docker compose up -d
docker compose ps   # wait for all four services to report "healthy"
```

Apply migrations if the backend image does not already (from `backend/`, with Compose Postgres
up): `uv run alembic upgrade head` (includes migration `0005` for
`research_assessment_snapshots`).

Then visit <http://localhost:3000/login> and sign in with the bootstrap credentials from
`.env` (`AEGIS_OPERATOR_USERNAME` / `AEGIS_OPERATOR_PASSWORD`; defaults in `.env.example`).
Those env values seed the first operator only when the `operators` table is empty. Or check
liveness with `curl http://localhost:8000/ready` (no auth required).

See [docs/operations/local-development.md](docs/operations/local-development.md) for the full
day-to-day workflow (including login and cookie flow), [docs/operations/configuration.md](docs/operations/configuration.md) for
every environment variable, and [docs/architecture/overview.md](docs/architecture/overview.md)
for the system architecture and module boundaries.

## Repository layout

| Path | Purpose |
| --- | --- |
| `backend/` | Python/FastAPI service (`uv`-managed). See [backend/README.md](backend/README.md). |
| `frontend/` | Next.js/TypeScript application (`pnpm`-managed). |
| `docker/`, `docker-compose.yml` | Local Compose topology and Dockerfiles. |
| `docker/nas/` | NAS Compose overlays, optional TLS proxy templates, runbook, and package/deploy/verify scripts (Phases 7–9). |
| `tests/integration/` | Cross-service tests run against the real Compose stack. |
| `docs/architecture/` | System design, data-model, and market-data contracts. |
| `docs/operations/` | Configuration, local development, CI, and security-scanning docs. |
| `.github/workflows/` | CI (see [docs/operations/ci.md](docs/operations/ci.md)). |
| `scripts/`, `prompts/` | Reserved, intentionally empty placeholders for later phases. |

## Quality gates

| Check | Command |
| --- | --- |
| Backend lint | `cd backend && uv run ruff check .` |
| Backend type-check | `cd backend && uv run pyright` |
| Backend tests | `cd backend && uv run pytest` |
| Frontend lint | `cd frontend && pnpm lint` |
| Frontend type-check | `cd frontend && pnpm exec tsc --noEmit` |
| Frontend tests | `cd frontend && pnpm test` |
| Frontend build | `cd frontend && pnpm build` |
| Integration tests | `docker compose up -d && uv run --project backend pytest tests/integration` |
| Security scans | See [docs/operations/security-scanning.md](docs/operations/security-scanning.md) |

## Developing with Cursor

1. Open this repository in Cursor.
2. Start a new Agent chat and select a Claude model.
3. Ask Claude to read `CLAUDE.md` and the project rules before planning or changing code.
