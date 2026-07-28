# AEGIS 3.0

AEGIS 3.0 is a greenfield, self-hosted market decision-support platform. It is decision-support
software only: it never places or transmits live orders (see [CLAUDE.md](CLAUDE.md) and
[.cursor/rules/aegis-project.mdc](.cursor/rules/aegis-project.mdc) for the full project rules).

Development starts locally in this repository. Deployment to the UGREEN NAS is performed only
after the current phase passes its documented local acceptance gate.

**Current phase: Phase 1 (market data ingestion - Alpha Vantage daily bars).** No scoring,
recommendation, prediction, or trading logic exists yet; Phase 1 adds the first real provider
integration and a validated, append-only observation store behind an on-demand ingestion
endpoint. See
[docs/architecture/decisions/0002-phase-1-market-data-ingestion.md](docs/architecture/decisions/0002-phase-1-market-data-ingestion.md)
and [CHANGELOG.md](CHANGELOG.md).

## Quick start

```sh
cp .env.example .env

cd backend && uv sync --all-groups && cd ..
cd frontend && pnpm install && cd ..

docker compose up -d
docker compose ps   # wait for all four services to report "healthy"
```

Then visit <http://localhost:3000> (frontend) or `curl http://localhost:8000/ready` (backend).

See [docs/operations/local-development.md](docs/operations/local-development.md) for the full
day-to-day workflow, [docs/operations/configuration.md](docs/operations/configuration.md) for
every environment variable, and [docs/architecture/overview.md](docs/architecture/overview.md)
for the system architecture and module boundaries.

## Repository layout

| Path | Purpose |
| --- | --- |
| `backend/` | Python/FastAPI service (`uv`-managed). See [backend/README.md](backend/README.md). |
| `frontend/` | Next.js/TypeScript application (`pnpm`-managed). |
| `docker/`, `docker-compose.yml` | Local Compose topology and Dockerfiles. |
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
