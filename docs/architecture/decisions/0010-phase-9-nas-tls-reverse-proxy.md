# ADR-0010: Phase 9 NAS Reverse-Proxy / TLS Packaging

- Status: Accepted
- Date: 2026-07-28

## Context

Phase 7 packaged the research-only authenticated stack for UGREEN NAS without a first-class
TLS termination path. Phase 4 session cookies support `AEGIS_SESSION_COOKIE_SECURE=true`, but
browsers only send Secure cookies over HTTPS. Operators need an optional reverse-proxy + TLS
profile so NAS deployments can keep Secure cookies without changing application auth.

This phase is packaging and operations only. It does not expand scoring, actionable states,
calibration, OAuth/MFA, orders, or a second market-data provider.

## Decisions

### 1. Prefer Caddy for the optional TLS profile

The optional reverse proxy is **Caddy** (`caddy:2-alpine`), not nginx.

Why Caddy:

- Built-in automatic HTTPS / ACME with minimal config when the NAS is reachable for issuance.
- Straightforward operator-supplied PEM mounting for air-gapped or private-CA deployments.
- Sensible default `X-Forwarded-*` behavior on `reverse_proxy` without large boilerplate.
- Smaller committed surface than a comparable nginx TLS + redirect + header template set.

nginx remains an acceptable operator substitute outside this repository if Caddy is awkward on
a particular NAS image policy; AEGIS documents and ships the Caddy profile only.

### 2. Optional Compose overlay; base NAS stack unchanged

TLS is an **optional** third Compose file:

```sh
docker compose \
  -f docker-compose.yml \
  -f docker/nas/docker-compose.nas.yml \
  -f docker/nas/docker-compose.nas.tls.yml \
  --env-file .env.nas \
  --project-directory . \
  up -d
```

When `AEGIS_NAS_TLS_ENABLED=true`, package/deploy/validate/verify scripts include this overlay.
When false (default), Phase 7 direct port publishing behavior is unchanged.

The TLS overlay:

- Adds a `caddy` service publishing `${AEGIS_TLS_HTTPS_PORT:-443}` and optional
  `${AEGIS_TLS_HTTP_PORT:-80}` (HTTP→HTTPS redirect).
- Unpublishes backend/frontend host ports (`ports: !reset []`) so API and console are reachable
  only through the proxy on the NAS host.

Local development Compose remains HTTP with `AEGIS_SESSION_COOKIE_SECURE=false`.

### 3. Application sessions remain the only auth model

The proxy terminates TLS and routes only. It must **not** introduce HTTP Basic Auth or replace
Phase 4 httpOnly session cookies. `/health` and `/ready` stay publicly reachable through the
proxy path operators expose; watchlist, daily-bars, and research routes stay session-gated.

### 4. Certificates: operator files and/or ACME; no committed PEMs

Two documented modes via `AEGIS_TLS_MODE`:

| Mode | Caddyfile template | Material |
| --- | --- | --- |
| `files` (default) | `docker/nas/proxy/Caddyfile.files` | Operator-supplied PEMs under `AEGIS_TLS_CERTS_DIR` |
| `acme` | `docker/nas/proxy/Caddyfile.acme` | Public DNS + ACME email; Caddy stores issued material in a named volume |

Committed repository content uses placeholders and empty cert directories only. Never commit
`.pem`, `.crt`, or `.key` material.

### 5. Dual-host routing aligned with CORS credentials

Default templates terminate TLS for two hostnames:

- `AEGIS_TLS_FRONTEND_HOST` → `frontend:3000`
- `AEGIS_TLS_API_HOST` → `backend:8000`

This matches the existing cross-origin console design (`NEXT_PUBLIC_API_BASE_URL` +
`AEGIS_CORS_ORIGINS` with credentials). Operators may customize the Caddyfile for path-based
single-host layouts, but must keep cookie Secure, CORS origins, and public verify URLs
consistent.

### 6. Cookie / CORS / URL fail-closed alignment

When the TLS profile is selected:

- `AEGIS_SESSION_COOKIE_SECURE` must be `true`.
- `AEGIS_CORS_ORIGINS`, `NEXT_PUBLIC_API_BASE_URL`, `AEGIS_NAS_API_BASE_URL`, and
  `AEGIS_NAS_FRONTEND_BASE_URL` must use `https://` origins that match the operator-facing
  hostnames.

Mismatch (Secure cookie with HTTP browser origins, or TLS enabled without required hosts /
file-mode PEMs) is a fail-closed packaging/validation error. Browsers will not send Secure
cookies on plain HTTP; CORS credentials will fail if origins do not match.

### 7. Forwarded headers; trust the Compose-network proxy

Caddy’s `reverse_proxy` sets `X-Forwarded-For`, `X-Forwarded-Proto`, and `X-Forwarded-Host`.
Uvicorn (backend image) honors proxy headers from the Docker network peer. No application code
change is required for Phase 4 Secure cookies because `secure=` is driven by
`AEGIS_SESSION_COOKIE_SECURE`, not by request scheme inference. Operators must still publish
HTTPS origins to the browser so the Secure flag is usable.

### 8. Upload ≠ verified; verify HTTPS when TLS is enabled

Package and deploy may transfer the TLS overlay and start Caddy. Verification remains a
separate mandatory step and, when TLS is enabled, must target the HTTPS operator-facing URLs
(and may use an explicit insecure-curl escape hatch only for lab self-signed certs).

## Consequences

- Operators can enable HTTPS on NAS with Secure session cookies without changing auth code.
- Direct `:8000`/`:3000` host exposure is removed when the TLS overlay is active.
- Local HTTP development is unchanged.
- ACME depends on outbound/inbound network reachability that many NAS LAN deployments lack;
  file-mode PEMs are the default documented path for private networks.

## Explicitly out of scope

- Live NAS deployment from this repository
- OAuth / MFA / RBAC / proxy Basic Auth
- Calibration, actionable promotion, recommendations, order placement
- Second market-data provider
- Committed hostnames, private IPs, certificates, or secrets
- Changing local development to HTTPS

## Related documents

- [0005-phase-4-operator-auth.md](0005-phase-4-operator-auth.md)
- [0008-phase-7-nas-deployment.md](0008-phase-7-nas-deployment.md)
- [../../../docker/nas/README.md](../../../docker/nas/README.md)
- [../../operations/nas-deployment.md](../../operations/nas-deployment.md)
- [../../operations/configuration.md](../../operations/configuration.md)
