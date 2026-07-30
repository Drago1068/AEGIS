# NAS Lab TLS Cutover and Rollback (Phase 40 / ADR-0041)

Lab HTTPS cutover for the UGREEN NAS using Phase 9 packaging. **Upload ≠ verified.**

## Lab profile

| Item | Value |
| --- | --- |
| Frontend | `https://aegis.local:18443` |
| API | `https://api.aegis.local:18443` |
| HTTP→HTTPS redirect listen | host `18080` |
| Cert mode | `files` (self-signed) |
| Overlay | `docker/nas/docker-compose.nas.tls.yml` |

### Hosts file (workstation)

```text
192.168.1.12  aegis.local api.aegis.local
```

Windows: `C:\Windows\System32\drivers\etc\hosts` (admin). Linux/macOS: `/etc/hosts`.

If hosts cannot be edited, scripted verify may use:

```text
AEGIS_NAS_VERIFY_CURL_RESOLVE=api.aegis.local:18443:192.168.1.12,aegis.local:18443:192.168.1.12
```

Browsers still need hosts (or equivalent DNS) for interactive console use.

## Prerequisites

1. Phase acceptance for the revision you will deploy.
2. Ports `18443` and `18080` free on the NAS (UGREEN often owns `80`/`443`).
3. Lab PEMs present under `docker/nas/proxy/certs/`:

```powershell
.\docker\nas\scripts\generate-lab-certs.ps1
```

```sh
./docker/nas/scripts/generate-lab-certs.sh
```

## Cutover

1. Update gitignored `.env.nas` (keep DB/operator secrets):

   - `AEGIS_NAS_TLS_ENABLED=true`
   - `AEGIS_TLS_MODE=files`
   - `AEGIS_TLS_FRONTEND_HOST=aegis.local`
   - `AEGIS_TLS_API_HOST=api.aegis.local`
   - `AEGIS_TLS_HTTPS_PORT=18443`
   - `AEGIS_TLS_HTTP_PORT=18080`
   - `AEGIS_TLS_CADDYFILE=./docker/nas/proxy/Caddyfile.files`
   - `AEGIS_TLS_CERTS_DIR=./docker/nas/proxy/certs`
   - `AEGIS_SESSION_COOKIE_SECURE=true`
   - `AEGIS_CORS_ORIGINS=https://aegis.local:18443`
   - `NEXT_PUBLIC_API_BASE_URL=https://api.aegis.local:18443`
   - `AEGIS_NAS_API_BASE_URL=https://api.aegis.local:18443`
   - `AEGIS_NAS_FRONTEND_BASE_URL=https://aegis.local:18443`
   - `AEGIS_NAS_VERIFY_CURL_INSECURE=true` (lab self-signed only)

2. Sync source + PEMs to the NAS; ensure `.env.nas` is copied into the build tree.

3. Native rebuild/up **with** the TLS overlay:

```sh
docker compose \
  -f docker-compose.yml \
  -f docker/nas/docker-compose.nas.yml \
  -f docker/nas/docker-compose.nas.tls.yml \
  --env-file .env.nas \
  --project-directory . \
  build

docker compose \
  -f docker-compose.yml \
  -f docker/nas/docker-compose.nas.yml \
  -f docker/nas/docker-compose.nas.tls.yml \
  --env-file .env.nas \
  --project-directory . \
  up -d --remove-orphans
```

Frontend must rebuild so `NEXT_PUBLIC_API_BASE_URL` is the HTTPS API origin.

4. Confirm direct `:18000` / `:13000` no longer serve API/console; `:18443` does.

5. Live verify from the workstation:

```powershell
.\docker\nas\scripts\verify.ps1
```

Retain stdout as evidence. Dry-run is **not** acceptance.

## Rollback

1. Set in `.env.nas`:

   - `AEGIS_NAS_TLS_ENABLED=false`
   - `AEGIS_SESSION_COOKIE_SECURE=false`
   - `AEGIS_CORS_ORIGINS=http://192.168.1.12:13000`
   - `NEXT_PUBLIC_API_BASE_URL=http://192.168.1.12:18000`
   - `AEGIS_NAS_API_BASE_URL=http://192.168.1.12:18000`
   - `AEGIS_NAS_FRONTEND_BASE_URL=http://192.168.1.12:13000`
   - `AEGIS_API_PORT=18000` / `FRONTEND_PORT=13000`
   - Remove or set `AEGIS_NAS_VERIFY_CURL_INSECURE=false`

2. Rebuild/up **without** the TLS overlay (two `-f` files only).

3. Run `verify.ps1` against HTTP bases; retain evidence.

## Related

- [ADR-0041](../architecture/decisions/0041-phase-40-nas-lab-tls-cutover.md)
- [ADR-0010](../architecture/decisions/0010-phase-9-nas-tls-reverse-proxy.md)
- [nas-live-verification.md](nas-live-verification.md)
