# ADR-0008: Phase 7 UGREEN NAS Deployment Packaging

- Status: Accepted
- Date: 2026-07-28

## Context

Phases 0 through 6 delivered a research-only, authenticated local stack with Compose, CI
build-only `linux/amd64` validation, and an explicit NAS deployment boundary that forbade
hostnames, credentials, and live deploy scripts in-repo.

Phase 7 packages that stack for UGREEN NAS DXP-series hardware without expanding product
capabilities: no actionable promotion, calibration, scheduled assessments, second provider,
orders, OAuth, MFA, or RBAC.

## Decisions

### 1. Compose overlay (not a fork)

NAS topology lives at `docker/nas/docker-compose.nas.yml` and is always combined with the
root `docker-compose.yml`:

```sh
docker compose -f docker-compose.yml -f docker/nas/docker-compose.nas.yml --env-file .env.nas ...
```

The overlay overrides restart policy, binds Postgres/Redis to the Compose network only
(no published host ports), pins `platform: linux/amd64`, sets production-leaning defaults,
and tags images for save/load. Local Compose remains the source of truth for service
definitions.

### 2. All NAS-specific values from env / gitignored config

Committed template: `.env.nas.example` (placeholders only). Runtime file: `.env.nas`
(gitignored). Scripts fail closed if required variables are missing. No hostname, private
IP, credential, SSH key, or private filesystem path may appear in committed files.

### 3. Auth mandatory and stricter on NAS

Session cookie auth (Phase 4) is unchanged in mechanism. On NAS:

- `AEGIS_OPERATOR_PASSWORD` must be a non-default value (not the local development
  placeholder); package/deploy scripts reject known placeholders.
- `AEGIS_SESSION_COOKIE_SECURE=true` when the operator console is served over HTTPS
  (documented default in `.env.nas.example`).
- `/health` and `/ready` remain public; watchlist, daily-bars, and research routes stay
  session-gated (401 without a session).

No OAuth, MFA, or RBAC.

### 4. Scripts: package, deploy, verify

Under `docker/nas/scripts/`:

| Step | Purpose |
| --- | --- |
| `package` | Build `linux/amd64` images, write a transferrable package. |
| `deploy` | Transfer package + gitignored `.env.nas` via SSH/SCP; load images; start stack; apply Alembic through `0005`. |
| `verify` | Prove live health, readiness, auth gate, key routes, frontend reachability; guide log inspection. |

PowerShell (`.ps1`) is the primary path from a Windows workstation. Portable shell (`.sh`)
mirrors the same steps for Git Bash, WSL, or on-NAS execution. A successful upload is not a
verified deployment; `verify` is mandatory and separate.

### 5. Platform `linux/amd64`

Per ADR-0001: UGREEN NAS DXP-series target is Intel x86_64. Package and overlay builds use
`--platform linux/amd64` / `platform: linux/amd64`.

### 6. Frontend API base URL at image build time

`NEXT_PUBLIC_API_BASE_URL` is inlined by Next.js at build time. The frontend Dockerfile
accepts it as a build arg; NAS package builds must supply the operator-facing API origin from
`.env.nas` (never a committed hostname).

### 7. Migrations on first start

Deploy (and the runbook) run `alembic upgrade head` inside the backend container so schema
includes migration `0005` (`research_assessment_snapshots`). Verify checks that current
revision is at head when SSH access is configured.

## Consequences

- Operators can package, transfer, start, and independently verify AEGIS on a NAS using only
  environment-sourced connection details.
- Local development Compose is unchanged for day-to-day work.
- Product scope remains research-only decision support; NAS packaging does not enable trading
  or actionable states.

## Explicitly out of scope

- Actionable promotion, calibration, scheduled research assessments
- Second market-data provider
- Order placement or transmission
- OAuth / MFA / multi-role RBAC
- Hardcoded NAS inventory (hosts, IPs, keys) in the repository
- Treating package upload as sufficient deployment evidence

## Related documents

- [../overview.md](../overview.md)
- [0001-phase-0-tooling.md](0001-phase-0-tooling.md)
- [0005-phase-4-operator-auth.md](0005-phase-4-operator-auth.md)
- [../../../docker/nas/README.md](../../../docker/nas/README.md)
- [../../operations/nas-deployment.md](../../operations/nas-deployment.md)
