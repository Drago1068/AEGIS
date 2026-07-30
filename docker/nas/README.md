# UGREEN NAS Deployment Runbook (Phase 7 + optional Phase 9 TLS)

AEGIS packages the existing Compose stack for UGREEN NAS DXP-series hardware
(`linux/amd64`, see ADR-0001 / ADR-0008). Product capabilities are unchanged: research-only
decision support with session auth. No orders or actionable promotion. Probability
calibration remains opt-in (`AEGIS_RESEARCH_CALIBRATION_AFTER_LABEL_ENABLED`, default false).

Optional **Phase 9** TLS termination (ADR-0010) adds a Caddy reverse-proxy overlay so
operators can serve HTTPS and keep `AEGIS_SESSION_COOKIE_SECURE=true`. The proxy is TLS +
routing only — **not** Basic Auth.

**Phase 17** hardens live verification (ADR-0018): upload is still not verification; use
`verify` after deploy and retain stdout as evidence. Dry-run is checklist-only and is **not**
acceptance evidence. See [../../docs/operations/nas-live-verification.md](../../docs/operations/nas-live-verification.md).

## Which scripts to use

| Host | Scripts |
| --- | --- |
| Windows workstation (primary) | `docker/nas/scripts/*.ps1` (PowerShell 7+ recommended) |
| Git Bash / WSL / Linux / on-NAS | `docker/nas/scripts/*.sh` |

All scripts **fail closed** if required environment variables are missing. NAS connection
details and secrets come only from a gitignored `.env.nas` (never from committed files).

## Prerequisites

1. Local Phase quality gates pass for the revision you intend to deploy (through Phase 16+
   for calibration readiness routes).
2. Docker with Buildx on the packaging machine; Docker Compose v2+ on the NAS.
3. SSH access to the NAS (OpenSSH `ssh` / `scp` on the workstation).
4. Copy `.env.nas.example` → `.env.nas` and replace every placeholder:
   - Strong non-default `AEGIS_OPERATOR_PASSWORD` and `POSTGRES_PASSWORD`
   - Operator-facing `NEXT_PUBLIC_API_BASE_URL`, `AEGIS_CORS_ORIGINS`, verify URLs
   - SSH host/user/remote directory (no real values belong in git)
5. When the console is served over HTTPS, keep `AEGIS_SESSION_COOKIE_SECURE=true`.
6. For research corpus growth (Phase 53 / ADR-0054), keep `AEGIS_DAILY_BAR_OUTPUT_SIZE=full`
   (example default). After changing from `compact` on an existing NAS, recreate the backend
   and run on-demand or scheduled ingest so append-only storage can grow with older bars.
7. For optional TLS (Phase 9): set `AEGIS_NAS_TLS_ENABLED=true`, hostnames, and either
   operator PEMs (`AEGIS_TLS_MODE=files`) or ACME email (`AEGIS_TLS_MODE=acme`).

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
baked into the frontend image at build time. TLS Caddy templates are always staged; the TLS
Compose overlay is included in compose validation when `AEGIS_NAS_TLS_ENABLED=true`.

### 2. Deploy (transfer + start)

```powershell
.\docker\nas\scripts\deploy.ps1
```

```sh
./docker/nas/scripts/deploy.sh
```

Deploys over SSH/SCP using `AEGIS_NAS_SSH_*` and `AEGIS_NAS_REMOTE_DIR` from `.env.nas`:

1. Copy compose overlays, proxy templates, scripts, image tarball, and `.env.nas`
2. When TLS files mode: copy operator PEMs into `docker/nas/proxy/certs/` on the NAS
3. `docker load` on the NAS
4. `docker compose ... up -d --no-build` (adds TLS overlay when enabled)
5. `alembic upgrade head` inside the backend container (includes migration `0008`)

This step proves upload and start only. It does **not** replace verify.

### 3. Verify (mandatory — Phase 17)

```powershell
.\docker\nas\scripts\verify.ps1
.\docker\nas\scripts\verify.ps1 -DryRun   # checklist only; NOT live evidence
```

```sh
./docker/nas/scripts/verify.sh
./docker/nas/scripts/verify.sh --dry-run   # checklist only; NOT live evidence
```

Checks against `AEGIS_NAS_API_BASE_URL` / `AEGIS_NAS_FRONTEND_BASE_URL` (symbol from
`AEGIS_NAS_VERIFY_SYMBOL`, default `AAPL`):

| Check | Expectation |
| --- | --- |
| `GET /health` | 200 |
| `GET /ready` | 200 |
| Unauthenticated watchlist / daily-bars / research latest / **calibration-readiness** | 401 |
| Frontend base URL | 200 or redirect |
| `POST /auth/login` + cookie | 200 |
| Authenticated `GET /research/{symbol}/calibration-readiness` | 200 |
| Authenticated `GET /research/{symbol}/assessments/latest` | 200 or 404 |
| `alembic current` (when SSH configured) | includes **`0008`** / head |

When TLS is enabled, verify URLs must be `https://`. For lab self-signed certs only, set
`AEGIS_NAS_VERIFY_CURL_INSECURE=true` (never for production trust decisions).

Full checklist: [../../docs/operations/nas-live-verification.md](../../docs/operations/nas-live-verification.md).

Log guidance (print from verify, or run on the NAS):

```sh
docker compose -f docker-compose.yml -f docker/nas/docker-compose.nas.yml \
  -f docker/nas/docker-compose.nas.tls.yml --env-file .env.nas \
  --project-directory . logs --tail=200 backend
# (omit the TLS compose file when AEGIS_NAS_TLS_ENABLED=false)
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

## Optional TLS profile (Phase 9 / ADR-0010)

Prefer **Caddy** for simpler TLS/ACME than nginx. Enable with:

```env
AEGIS_NAS_TLS_ENABLED=true
AEGIS_TLS_MODE=files   # or acme
AEGIS_TLS_FRONTEND_HOST=...
AEGIS_TLS_API_HOST=...
AEGIS_SESSION_COOKIE_SECURE=true
```

Compose when enabled:

```sh
docker compose \
  -f docker-compose.yml \
  -f docker/nas/docker-compose.nas.yml \
  -f docker/nas/docker-compose.nas.tls.yml \
  --env-file .env.nas --project-directory . up -d
```

Behavior:

- Publishes 443 (+ optional 80→HTTPS redirect); unpublishes API/frontend host ports
- Routes `AEGIS_TLS_FRONTEND_HOST` → `frontend:3000`, `AEGIS_TLS_API_HOST` → `backend:8000`
- Sets `X-Forwarded-*` via Caddy `reverse_proxy`
- **files** mode: PEMs at `AEGIS_TLS_CERTS_DIR` (`frontend.crt/.key`, `api.crt/.key`)
- **acme** mode: public DNS + `AEGIS_TLS_ACME_EMAIL`; issued material in `caddy_data` volume

### Cookie / CORS alignment (fail closed)

| Setting | Required when TLS enabled |
| --- | --- |
| `AEGIS_SESSION_COOKIE_SECURE` | `true` |
| `AEGIS_CORS_ORIGINS` | `https://` console origin(s) |
| `NEXT_PUBLIC_API_BASE_URL` | `https://` API origin (baked at package time) |
| Verify base URLs | `https://` |

If Secure is true but the browser uses `http://`, cookies are not sent and login fails.
Package/validate/deploy scripts reject HTTP public origins when the TLS profile is selected.

Templates and cert directory notes: [proxy/README.md](proxy/README.md).

## Migrations (first start)

Deploy runs `alembic upgrade head` after containers start. Head as of Phase 15+ includes:

- `0004` — `operators`
- `0005` — `research_assessment_snapshots`
- `0006` — provider historical corrections columns
- `0007` — `research_assessment_outcome_labels`
- `0008` — `research_assessment_probability_calibrations`

If you start the stack manually, run the same `exec ... alembic upgrade head` before calling
verify. Phase 17 verify expects `0008` or `head` when SSH is configured.

## Local dry-run (no NAS)

Validate overlay interpolation without contacting a NAS:

```powershell
.\docker\nas\scripts\validate-local.ps1
.\docker\nas\scripts\validate-local.ps1 -Tls
# Optional amd64 build (requires a real `.env.nas`, not placeholders):
.\docker\nas\scripts\validate-local.ps1 -BuildImages
```

```sh
./docker/nas/scripts/validate-local.sh
./docker/nas/scripts/validate-local.sh --tls
./docker/nas/scripts/validate-local.sh --build-images
```

`--tls` / `-Tls` forces the TLS overlay dry-run (or set `AEGIS_NAS_TLS_ENABLED=true`). With
`.env.nas.example`, PEM presence is not enforced (compose config only). With a real `.env.nas`
and `files` mode, missing PEMs fail closed.

CI validates the base NAS overlay and a TLS overlay `docker compose config` using ACME-mode
placeholders (no PEMs, no live NAS).

## Safety rules

- No NAS hostname, private IP, credential, SSH key, private path, or TLS PEM in committed files.
- `.env.nas` is gitignored; only `.env.nas.example` placeholders are committed.
- Package/deploy reject known development/template operator and database passwords.
- Auth remains session-cookie based; do not weaken gates for NAS convenience.
- Proxy must not become the auth model (no Basic Auth substitution).

## Related documents

- [ADR-0008](../../docs/architecture/decisions/0008-phase-7-nas-deployment.md)
- [ADR-0010](../../docs/architecture/decisions/0010-phase-9-nas-tls-reverse-proxy.md)
- [docs/operations/nas-deployment.md](../../docs/operations/nas-deployment.md)
- [docs/operations/configuration.md](../../docs/operations/configuration.md)
- [ADR-0001](../../docs/architecture/decisions/0001-phase-0-tooling.md) (platform assumption)
