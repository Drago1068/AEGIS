# NAS Deployment (Phase 7 + optional Phase 9 TLS + Phase 17 live verify)

Operator-facing summary of UGREEN NAS packaging. The authoritative runbook is
[../../docker/nas/README.md](../../docker/nas/README.md). Live verify checklist:
[nas-live-verification.md](nas-live-verification.md). Architecture decisions:
[../architecture/decisions/0008-phase-7-nas-deployment.md](../architecture/decisions/0008-phase-7-nas-deployment.md),
[../architecture/decisions/0010-phase-9-nas-tls-reverse-proxy.md](../architecture/decisions/0010-phase-9-nas-tls-reverse-proxy.md),
[../architecture/decisions/0018-phase-17-nas-live-verification.md](../architecture/decisions/0018-phase-17-nas-live-verification.md).

## Boundary

- Compose **overlay** at `docker/nas/docker-compose.nas.yml` extends the root
  `docker-compose.yml` (not a forked stack).
- Optional TLS overlay: `docker/nas/docker-compose.nas.tls.yml` (Caddy) when
  `AEGIS_NAS_TLS_ENABLED=true`.
- All NAS-specific values live in gitignored `.env.nas` (template: `.env.nas.example`).
- Scripts: `docker/nas/scripts/package|deploy|verify` (PowerShell primary on Windows; `.sh`
  for Git Bash/WSL/NAS).
- **Upload ≠ verified deployment.** Always run verify after deploy (ADR-0018). Dry-run is
  checklist-only and is not acceptance evidence.

## Quick commands (Windows)

```powershell
cp .env.nas.example .env.nas   # then edit placeholders
.\docker\nas\scripts\validate-local.ps1
.\docker\nas\scripts\validate-local.ps1 -Tls   # optional Phase 9 overlay dry-run
.\docker\nas\scripts\package.ps1
.\docker\nas\scripts\deploy.ps1
.\docker\nas\scripts\verify.ps1
.\docker\nas\scripts\verify.ps1 -DryRun   # planning only; not live evidence
```

## Auth on NAS

Session cookie auth is mandatory. Use a non-default `AEGIS_OPERATOR_PASSWORD`. Set
`AEGIS_SESSION_COOKIE_SECURE=true` when serving over HTTPS. No OAuth/MFA/RBAC. The TLS
proxy does not replace application sessions (no Basic Auth).

## Optional HTTPS (Phase 9)

1. Set `AEGIS_NAS_TLS_ENABLED=true` and hostnames (`AEGIS_TLS_FRONTEND_HOST` /
   `AEGIS_TLS_API_HOST`).
2. Choose `AEGIS_TLS_MODE=files` (operator PEMs under `AEGIS_TLS_CERTS_DIR`) or `acme`.
3. Align `AEGIS_CORS_ORIGINS`, `NEXT_PUBLIC_API_BASE_URL`, and verify URLs to `https://`.
4. Package/deploy/verify; confirm HTTPS paths. Upload alone is still not verification.

Mismatch of Secure cookies with HTTP origins fails closed in packaging scripts — browsers
will not send Secure cookies on plain HTTP.

## Migrations

First start (via deploy script) runs `alembic upgrade head` in the backend container,
through revision `0008` (`research_assessment_probability_calibrations`). Verify confirms
current revision when SSH is configured.

## Local dry-run without a NAS

`validate-local` runs `docker compose ... config` for the overlay. Pass `-Tls` / `--tls` to
include the TLS overlay. Optional `-BuildImages` / `--build-images` builds `linux/amd64`
images only when a real `.env.nas` is present.

`verify -DryRun` / `--dry-run` prints the live-verify checklist without contacting the NAS
and is **not** evidence of a verified deployment.
