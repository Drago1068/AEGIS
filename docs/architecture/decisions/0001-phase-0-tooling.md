# ADR-0001: Phase 0 Tooling and Directory Decisions

- Status: Accepted
- Date: 2026-07-27

## Context

`CLAUDE.md` and the project rules pin the major frameworks (FastAPI, SQLAlchemy, Alembic,
Pydantic, pytest, PostgreSQL/TimescaleDB, Redis, Next.js, TypeScript, Tailwind CSS, Docker
Compose) but leave several concrete choices open: dependency/package managers, exact language
versions, the type-checking gate, and the responsibility of a few scaffold directories that
were ambiguous in the initial repository layout (`database/`, root `tests/`). This ADR
records those decisions so they are not re-litigated implicitly file-by-file.

## Decisions

### 1. Backend dependency management: uv

`uv` manages the backend Python environment and dependencies. Files: `backend/pyproject.toml`
(project metadata and dependency groups), a committed `backend/uv.lock` (exact resolved
versions), and `backend/.python-version` (pins the interpreter uv provisions).

Rationale: uv provides fast, reproducible, single-tool dependency resolution, virtual
environment management, and Python interpreter provisioning (it can install the pinned Python
version itself, removing a manual setup step). Alternatives considered: Poetry (mature but
slower and requires a separate Python installation), pip + pip-tools (minimal but more manual
lockfile/venv plumbing).

### 2. Python version: pinned to 3.12 exactly

`backend/pyproject.toml` sets `requires-python = "==3.12.*"` (not an open-ended `>=3.12`).
`backend/.python-version` contains `3.12`. The backend container image and the CI job both
target the same `3.12` line, so local dev, CI, and the production image cannot silently drift
onto different minor Python versions.

### 3. Frontend package management: pnpm, with pinned Node LTS

`pnpm` manages frontend dependencies (committed `pnpm-lock.yaml`). `frontend/package.json`
declares `"packageManager": "pnpm@11.9.0"` (Corepack-enforced). A `.node-version` file at the
frontend root (`24.14.0`, the resolved Node 24 LTS patch used at implementation time) pins the
exact Node version used for local dev, CI, and the frontend container base image
(`docker/frontend.Dockerfile`).

Rationale: pnpm is disk-efficient and enforces strict dependency resolution (no phantom
dependencies), which suits a long-lived, security-conscious project. Alternatives considered:
npm (simplest, zero extra install, but weaker resolution guarantees), Yarn.

### 4. Backend type-checking gate: Pyright strict, exclusively

CI and local pre-merge checks run `pyright` in strict mode via `uv run pyright` (Pyright is
PyPI-distributed and added as a uv dev-dependency, so no separate Node toolchain is required
for the backend). No mypy job exists. This matches the repository's existing
`.vscode/settings.json` (`"python.analysis.typeCheckingMode": "strict"`), so the editor
(Pylance, which embeds Pyright) and CI enforce identical type rules with no second source of
truth.

### 5. Database/migrations directory: `backend/alembic/` only

`backend/alembic/` is the single authoritative location for all schema management, including
enabling and verifying the TimescaleDB extension. The root `database/` placeholder directory
(empty and untracked) is not populated; its would-be responsibilities (schema migrations) are
fully absorbed into `backend/alembic/` to avoid two competing locations for the same concern.

### 6. Root `tests/` directory: cross-service integration and acceptance tests only

Root `tests/` (specifically `tests/integration/`) is reserved for tests that require the full
Docker Compose stack running - for example a readiness-endpoint test that exercises real
Postgres/TimescaleDB and Redis containers. Backend unit tests live in `backend/tests/`;
frontend unit tests live under `frontend/`. This keeps the fast unit-test suites colocated
with their service while giving cross-service tests one clear home.

### 7. NAS target architecture assumption

UGREEN NAS DXP-series hardware (the deployment target referenced in the project rules) uses
Intel x86_64 processors. Phase 0's build-only architecture validation therefore targets
`linux/amd64`. If a different specific NAS model with a different CPU architecture is used,
this is a one-line change to the `docker buildx build --platform ...` target, recorded here
and in `docker/nas/README.md`.

### 8. File encoding

All repository files are UTF-8 without a byte-order mark. Plain ASCII punctuation (hyphens,
straight quotes) is used in documentation and code instead of em dashes or smart quotes, to
avoid encoding artifacts (mojibake) when files are viewed or edited across different tools and
locales on Windows.

## Consequences

- Local setup requires `uv` and Node with Corepack (for the pinned `pnpm` version) but no
  manually pre-installed Python 3.12 or global pnpm install; both are provisioned by their
  respective lockfile-driven tools.
- Any future change to a decision in this ADR (for example switching from Pyright to mypy, or
  from uv to Poetry) requires a new, superseding ADR rather than an ad hoc change, per the
  project rule that architecture defaults may only change through a documented decision.

## Related documents

- [../overview.md](../overview.md)
- [../data-model.md](../data-model.md)
- [../market-data-contracts.md](../market-data-contracts.md)
