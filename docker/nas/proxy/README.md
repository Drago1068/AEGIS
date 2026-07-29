# TLS proxy templates (Phase 9 / ADR-0010)

Optional Caddy configuration for the NAS TLS Compose overlay
(`docker/nas/docker-compose.nas.tls.yml`). The proxy terminates TLS and routes to
`frontend:3000` / `backend:8000` only. **Do not** add Basic Auth here — application
session cookies (Phase 4) remain the auth model.

## Templates

| File | When to use |
| --- | --- |
| `Caddyfile.files` | Operator-supplied PEMs (default; typical private NAS LAN) |
| `Caddyfile.acme` | Public DNS + ACME when the NAS can complete HTTP-01/TLS-01 |

Select via `.env.nas`:

- `AEGIS_TLS_MODE=files` → `AEGIS_TLS_CADDYFILE=./proxy/Caddyfile.files`
- `AEGIS_TLS_MODE=acme` → `AEGIS_TLS_CADDYFILE=./proxy/Caddyfile.acme`

Paths in the TLS Compose file are relative to `docker/nas/`.

## Certificates directory

Mount operator PEMs with `AEGIS_TLS_CERTS_DIR` (default `./proxy/certs`). For `files` mode
provide:

| Path in container | Purpose |
| --- | --- |
| `/certs/frontend.crt` + `/certs/frontend.key` | Console hostname |
| `/certs/api.crt` + `/certs/api.key` | API hostname |

Never commit real `.crt` / `.key` / `.pem` files. See `certs/README.md`.

## Forwarded headers

Caddy `reverse_proxy` forwards `X-Forwarded-For`, `X-Forwarded-Proto`, and
`X-Forwarded-Host`. Keep `AEGIS_SESSION_COOKIE_SECURE=true` and publish `https://`
origins in `AEGIS_CORS_ORIGINS`, `NEXT_PUBLIC_API_BASE_URL`, and verify base URLs.
