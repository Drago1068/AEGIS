# ADR-0041: Phase 40 NAS Lab TLS Live Cutover

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 9 packaged an optional Caddy TLS overlay (ADR-0010). Live NAS verification through
Phase 39 used plain HTTP on remapped ports (`18000` / `13000`). Operators need a verified
lab cutover to HTTPS with Secure session cookies without ACME or public DNS.

## Decisions

### 1. Lab profile (locked)

| Setting | Value |
| --- | --- |
| Frontend host | `aegis.local` |
| API host | `api.aegis.local` |
| HTTPS publish | `18443` → container `443` |
| HTTP redirect publish | `18080` → container `80` |
| Mode | `files` (self-signed PEMs) |
| Verify | HTTPS bases + `AEGIS_NAS_VERIFY_CURL_INSECURE=true` |

Workstation (and any browser client) should resolve:

```text
192.168.1.12  aegis.local api.aegis.local
```

Or set `AEGIS_NAS_VERIFY_CURL_RESOLVE` for scripted verify without hosts edits (see cutover doc).

### 2. Overlay behavior unchanged

`AEGIS_NAS_TLS_ENABLED=true` includes `docker/nas/docker-compose.nas.tls.yml`, which
unpublishes backend/frontend host ports. Clients must use Caddy on `18443`.

### 3. Non-443 redirect

`Caddyfile.files` redirects HTTP to `https://{host}:{$AEGIS_TLS_HTTPS_PORT}{uri}` so
remapped HTTPS ports work. `AEGIS_TLS_HTTPS_PORT` is passed into the Caddy container env.

### 4. Lab PEMs

`generate-lab-certs.ps1` / `generate-lab-certs.sh` write gitignored PEMs under
`docker/nas/proxy/certs/`. Never commit certificates or keys.

### 5. Upload ≠ verified

Redeploy alone is not acceptance. Retain `verify.ps1` / `verify.sh` HTTPS stdout. When TLS
is enabled and SSH is configured, confirm the `caddy` service is running.

### 6. Rollback

Documented in `docs/operations/nas-tls-cutover.md`: disable TLS flag, restore HTTP verify
URLs and `AEGIS_SESSION_COOKIE_SECURE=false`, republish `18000`/`13000`, rebuild frontend
for the HTTP API origin.

## Explicitly out of scope

- ACME / public DNS
- OAuth / MFA / proxy Basic Auth
- Multi-horizon calibration or other product features
- Default-on automatic calibration
- Actionable promotion, recommendations, orders

## Related documents

- [0010-phase-9-nas-tls-reverse-proxy.md](0010-phase-9-nas-tls-reverse-proxy.md)
- [../../operations/nas-tls-cutover.md](../../operations/nas-tls-cutover.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
