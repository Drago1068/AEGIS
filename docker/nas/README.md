# UGREEN NAS Deployment Runbook (Phase 7)

AEGIS 3.0 packages the existing Compose stack for UGREEN NAS DXP-series hardware
(`linux/amd64`, see ADR-0001 / ADR-0008). Product capabilities are unchanged: research-only
decision support with session auth. No orders, actionable promotion, calibration, second
provider, OAuth, MFA, or RBAC.

**Upload is not verification.** Package → transfer/start → verify are three separate steps.
A successful SCP/rsync or `docker compose up` alone is not a verified live deployment.

## Which scripts to use

| Host | Scripts |
| --- | --- |
| Windows workstation (primary) | `docker/nas/scripts/*.ps1` (PowerShell 7+ recommended) |
| Git Bash / WSL / Linux / on-NAS | `docker/nas/scripts/*.sh` |

All scripts **fail closed** if required environment variables are missing. NAS connection
details and secrets come only from a gitignored `.env.nas` (never from committed files).

## Prerequisites

1. Local Phase 0–6 quality gates pass for the revision you intend to deploy.
2. Docker with Buildx on the packaging machine; Docker Compose v2+ on the NAS.
3. SSH access to the NAS (OpenSSH `ssh` / `scp` on the workstation).
4. Copy `.env.nas.example` → `.env.nas` and replace every placeholder:
   - Strong non-default `AEGIS_OPERATOR_PASSWORD` and `POSTGRES_PASSWORD`
   - Operator-facing `NEXT_PUBLIC_API_BASE_URL`, `AEGIS_CORS_ORIGINS`, verify URLs
   - SSH host/user/remote directory (no real values belong in git)
5. When the console is served over HTTPS, keep `AEGIS_SESSION_COOKIE_SECURE=true`.

## Flow

```text
package  →  deploy (transfer + start + alembic)  →  verify
              ↑                                      ↑
         upload ≠ done                          acceptance evidence
```

### 1. Package (no NAS contact)

From the repository root, with `.env.nas` filled:

```powershell
.\docker\nas\scripts\package.ps1
```

```sh
./docker/nas/scripts/package.sh
```

This builds `linux/amd64` images, `docker save`s them, and stages
`docker/nas/dist/aegis-nas-package/` (plus a zip/tar archive). `NEXT_PUBLIC_API_BASE_URL` is
baked into the frontend image at build time.

### 2. Deploy (transfer + start)

```powershell
.\docker\nas\scripts\deploy.ps1
```

```sh
./docker/nas/scripts/deploy.sh
```

Deploys over SSH/SCP using `AEGIS_NAS_SSH_*` and `AEGIS_NAS_REMOTE_DIR` from `.env.nas`:

1. Copy compose overlay, scripts, image tarball, and `.env.nas`
2. `docker load` on the NAS
3. `docker compose ... up -d --no-build`
4. `alembic upgrade head` inside the backend container (includes migration `0005`)

This step proves upload and start only. It does **not** replace verify.

### 3. Verify (mandatory)

```powershell
.\docker\nas\scripts\verify.ps1
```

```sh
./docker/nas/scripts/verify.sh
```

Checks against `AEGIS_NAS_API_BASE_URL` / `AEGIS_NAS_FRONTEND_BASE_URL`:

| Check | Expectation |
| --- | --- |
| `GET /health` | 200 |
| `GET /ready` | 200 |
| `GET /watchlist` (no cookie) | 401 |
| `GET /market-data/AAPL/daily-bars` (no cookie) | 401 |
| `GET /research/AAPL/assessments/latest` (no cookie) | 401 |
| Frontend base URL | 200 or redirect |
| `alembic current` (when SSH configured) | includes `0005` / head |

Log guidance (print from verify, or run on the NAS):

```sh
docker compose -f docker-compose.yml -f docker/nas/docker-compose.nas.yml --env-file .env.nas \
  --project-directory . logs --tail=200 backend
docker compose -f docker-compose.yml -f docker/nas/docker-compose.nas.yml --env-file .env.nas \
  --project-directory . logs --tail=200 frontend
docker compose -f docker-compose.yml -f docker/nas/docker-compose.nas.yml --env-file .env.nas \
  --project-directory . ps
```

## Compose overlay

Never run the NAS file alone. Always combine with the root compose file:

```sh
docker compose -f docker-compose.yml -f docker/nas/docker-compose.nas.yml \
  --env-file .env.nas --project-directory . <command>
```

Overlay behavior (ADR-0008):

- `platform: linux/amd64` on all services
- `restart: always`
- Postgres/Redis host ports removed (Compose network only)
- Production-leaning defaults (`AEGIS_ENVIRONMENT=production`, Secure session cookie default)
- Image tags `aegis-backend:nas` / `aegis-frontend:nas` for save/load

## Migrations (first start)

Deploy runs `alembic upgrade head` after containers start. Head as of Phase 6/7 includes:

- `0004` — `operators`
- `0005` — `research_assessment_snapshots`

If you start the stack manually, run the same `exec ... alembic upgrade head` before calling
the deployment verified.

## Local dry-run (no NAS)

Validate overlay interpolation without contacting a NAS:

```powershell
.\docker\nas\scripts\validate-local.ps1
# Optional amd64 build (requires a real `.env.nas`, not placeholders):
.\docker\nas\scripts\validate-local.ps1 -BuildImages
```

```sh
./docker/nas/scripts/validate-local.sh
./docker/nas/scripts/validate-local.sh --build-images
```

CI continues to run build-only `linux/amd64` image builds and (as of Phase 7) validates the
NAS overlay `docker compose config` using `.env.nas.example`.

## Safety rules

- No NAS hostname, private IP, credential, SSH key, or private path in committed files.
- `.env.nas` is gitignored; only `.env.nas.example` placeholders are committed.
- Package/deploy reject known development/template operator and database passwords.
- Auth remains session-cookie based; do not weaken gates for NAS convenience.

## Related documents

- [ADR-0008](../../docs/architecture/decisions/0008-phase-7-nas-deployment.md)
- [docs/operations/nas-deployment.md](../../docs/operations/nas-deployment.md)
- [docs/operations/configuration.md](../../docs/operations/configuration.md)
- [ADR-0001](../../docs/architecture/decisions/0001-phase-0-tooling.md) (platform assumption)
