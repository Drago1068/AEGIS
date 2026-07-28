# Continuous Integration

`.github/workflows/ci.yml` defines five jobs. This document describes what each does, the local
command it wraps, and which parts of Phase 0 acceptance depend on a configured GitHub remote.

## Local-only vs. remote-dependent gates

Per [../../CLAUDE.md](../../CLAUDE.md) and the Phase 0 acceptance checklist, **Phase 0
acceptance is never contingent on GitHub Actions actually running.** `ci.yml` and any branch
protection rule only take effect once:

1. a GitHub remote is configured for this repository, and
2. a push or pull request against it triggers the workflow.

Every command each job runs is also listed in
[local-development.md](local-development.md#reproducible-command-reference) and
[security-scanning.md](security-scanning.md) so the same checks can be run and verified purely
from a local shell with no remote configured at all.

## Jobs

### `backend`

Mirrors the backend quality gates: `uv sync --locked --all-groups`, `uv run ruff check .`,
`uv run pyright`, `uv run pytest` (which includes the health/readiness contract tests and the
scoped no-domain-logic check).

### `frontend`

Mirrors the frontend quality gates: `pnpm install --frozen-lockfile`, `pnpm lint`,
`pnpm exec tsc --noEmit`, the no-domain-logic script, `pnpm test`, `pnpm build`.

### `compose-validate`

Runs `docker compose config` to validate the Compose topology, then does a **build-only**
`linux/amd64` build of both Dockerfiles (the UGREEN NAS DXP-series target architecture; see
[../architecture/decisions/0001-phase-0-tooling.md](../architecture/decisions/0001-phase-0-tooling.md)).
This never pushes, runs, or deploys anything; see [../../docker/nas/README.md](../../docker/nas/README.md)
for the full NAS deployment boundary.

### `integration`

Brings up the full Compose stack (`docker compose up -d --build`), waits for every service to
report `healthy`, then runs `tests/integration/` against the real containers (the readiness
healthy-path test). Depends on `backend`, `frontend`, and `compose-validate` passing first, so a
broken unit test or a broken image build fails fast before the slower integration job starts.
Logs are dumped on failure and the stack is always torn down (`docker compose down -v`) at the
end of the job.

### `security`

Runs all four Phase 0 security scans described in
[security-scanning.md](security-scanning.md): `pip-audit` (backend), `pnpm audit --prod`
(frontend), `gitleaks` (secrets, full history via `fetch-depth: 0`), and `trivy image` (both
built images). High/critical findings fail the job.

## Branch protection (once a remote exists)

When branch protection is configured on the GitHub remote, the recommended required checks are:

- `Backend (lint, type-check, test)`
- `Frontend (lint, type-check, test, build)`
- `Compose config + NAS-architecture build validation`
- `Integration (Docker Compose readiness, healthy path)`
- `Security scanning (dependencies, secrets, images)`

This is a recommendation to apply manually in the repository's GitHub settings; Phase 0 does not
script branch-protection configuration, since that is a remote/organizational setting outside
this repository's file tree.

## Action version policy

Third-party and first-party GitHub Actions in `ci.yml` are pinned to major-version tags (for
example `actions/checkout@v4`), which is the actively-maintained convention those actions
publish and support. This is a deliberate Phase 0 trade-off between reproducibility and
maintenance burden; pinning to full commit SHAs may be adopted in a later phase via a documented
decision if stricter supply-chain guarantees are required.
