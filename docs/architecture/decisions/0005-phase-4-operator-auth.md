# ADR-0005: Phase 4 Operator Authentication

- Status: Accepted
- Date: 2026-07-28

## Context

Phases 1-3 accepted unauthenticated watchlist and market-data APIs as a local/trusted-network
limitation. Phase 2 made unauthenticated watchlist changes affect scheduled ingestion, and
Phase 3 exposed those APIs through a browser console. Before charts, scoring, or NAS exposure,
AEGIS needs application-level authentication that fails closed on protected routes while
keeping orchestration health checks public.

## Decisions

### 1. Mechanism: httpOnly session cookie + Redis session store

Login with username/password creates a random session id stored in Redis (TTL from
`AEGIS_SESSION_TTL_SECONDS`) and set as an httpOnly cookie (`AEGIS_SESSION_COOKIE_NAME`).
Logout deletes the Redis key and clears the cookie. No JWT bearer tokens, OAuth, or
reverse-proxy-only Basic Auth as the application auth model.

### 2. Identity: single operator role

Table `operators` stores `id`, `username` (unique), `password_hash`, `created_at`,
`updated_at`. There is one operational role and no RBAC matrix in Phase 4.

### 3. Bootstrap: env credentials seed an empty operators table once

`AEGIS_OPERATOR_USERNAME` and `AEGIS_OPERATOR_PASSWORD` seed the first operator only when the
table is empty. The password is hashed with Argon2 at seed time and never logged. After any
row exists, env credentials are not re-applied (same pattern as watchlist seed in ADR-0003).

### 4. Protection surface

Require a valid session for all `/watchlist*` and `/market-data*` routes. Keep `/health` and
`/ready` public for Compose/CI. Auth routes: `POST /auth/login`, `POST /auth/logout`,
`GET /auth/me` (me requires a session).

### 5. CORS credentials

`CORSMiddleware` uses `allow_credentials=True` with the explicit `AEGIS_CORS_ORIGINS`
allow-list so the Next.js console can send cookies cross-origin. Wildcard origins are not
used.

### 6. Frontend

`/login` collects credentials; authenticated API calls use `credentials: "include"`; HTTP 401
redirects to login. In-process scheduled ingestion does not use HTTP auth (same process).

## Consequences

- Unauthenticated browser or curl access to watchlist/market-data returns 401.
- Development defaults use a non-production placeholder password documented in `.env.example`
  that must be changed before any non-local exposure.
- Future MFA/OAuth/RBAC requires a superseding ADR.

## Explicitly out of scope

- OAuth/SSO, MFA, password-reset email
- Multi-role authorization
- Charts, scoring, recommendations, order placement
- NAS deployment

## Related documents

- [../overview.md](../overview.md)
- [0003-phase-2-scheduled-watchlist.md](0003-phase-2-scheduled-watchlist.md)
- [0004-phase-3-operator-console.md](0004-phase-3-operator-console.md)
