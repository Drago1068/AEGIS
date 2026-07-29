# NAS Deployment (Phase 7)

Operator-facing summary of UGREEN NAS packaging. The authoritative runbook is
[../../docker/nas/README.md](../../docker/nas/README.md). Architecture decision:
[../architecture/decisions/0008-phase-7-nas-deployment.md](../architecture/decisions/0008-phase-7-nas-deployment.md).

## Boundary

- Compose **overlay** at `docker/nas/docker-compose.nas.yml` extends the root
  `docker-compose.yml` (not a forked stack).
- All NAS-specific values live in gitignored `.env.nas` (template: `.env.nas.example`).
- Scripts: `docker/nas/scripts/package|deploy|verify` (PowerShell primary on Windows; `.sh`
  for Git Bash/WSL/NAS).
- **Upload ≠ verified deployment.** Always run verify after deploy.

## Quick commands (Windows)

```powershell
cp .env.nas.example .env.nas   # then edit placeholders
.\docker\nas\scripts\validate-local.ps1
.\docker\nas\scripts\package.ps1
.\docker\nas\scripts\deploy.ps1
.\docker\nas\scripts\verify.ps1
```

## Auth on NAS

Session cookie auth is mandatory. Use a non-default `AEGIS_OPERATOR_PASSWORD`. Set
`AEGIS_SESSION_COOKIE_SECURE=true` when serving over HTTPS. No OAuth/MFA/RBAC in this phase.

## Migrations

First start (via deploy script) runs `alembic upgrade head` in the backend container,
including revision `0005` (`research_assessment_snapshots`). Verify confirms current
revision when SSH is configured.

## Local dry-run without a NAS

`validate-local` runs `docker compose ... config` for the overlay. Optional `-BuildImages` /
`--build-images` builds `linux/amd64` images only when a real `.env.nas` is present.
