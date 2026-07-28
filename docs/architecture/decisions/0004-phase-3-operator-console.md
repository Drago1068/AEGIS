# ADR-0004: Phase 3 Operator Console

- Status: Accepted
- Date: 2026-07-28

## Context

Phase 2 (ADR-0003) left the frontend on a Phase 0 placeholder and deferred a UI for managing
the database-backed watchlist. The backend already exposes `GET/POST/DELETE /watchlist`,
`POST /market-data/ingest`, and `GET /market-data/{symbol}/daily-bars`. Operators still need a
browser console to use those endpoints without calling the API directly. Browser calls from
the Next.js origin (`http://localhost:3000`) to the FastAPI origin (`http://localhost:8000`)
also cannot succeed until Cross-Origin Resource Sharing (CORS) is configured - Phase 0/1/2
never added `CORSMiddleware`.

## Decisions

### 1. Scope: frontend operator console over existing APIs

Phase 3 adds a Next.js operator console that consumes the existing Phase 1/2 HTTP contracts.
No new domain logic, providers, scoring, or trading endpoints are introduced. The console
surfaces three capabilities: watchlist management, on-demand ingest with a per-symbol
summary, and a recent daily-bar table for a selected symbol.

### 2. Routing: `/` console and `/symbols/[symbol]` bars

The home route is the console (watchlist + ingest). Symbol rows link to
`/symbols/[symbol]`, which renders a table of stored OHLCV bars (newest first). Navigation
stays minimal; schedule/cron configuration remains environment-driven (no schedule UI).

### 3. Daily bars as a table, not charts

Phase 3 uses an HTML table for stored bars. Chart libraries, technical indicators, and any
derived scoring remain out of scope so the slice stays reviewable and dependency-light.

### 4. CORS: environment-configured origins only

`AEGIS_CORS_ORIGINS` is a comma-separated list of allowed browser origins (default
`http://localhost:3000`). FastAPI's `CORSMiddleware` is registered from that list for the
methods and headers required by the console (`GET`, `POST`, `DELETE`, `OPTIONS`, plus
`Content-Type`). Origins are never hardcoded as production hostnames; operators set the
variable for their deployment.

### 5. Authentication: still none (limitation reaffirmed)

Watchlist, ingest, and bar-read endpoints remain unauthenticated, per ADR-0002/ADR-0003. The
console makes those endpoints easier to reach from a browser on the trusted local network;
this is the same accepted limitation with a larger convenience surface, not a new auth model.

## Consequences

- The frontend replaces the Phase 0 `NoDataMessage` placeholder with real operator flows.
- Backend changes in Phase 3 are limited to CORS settings + middleware (plus docs/tests).
- Future phases that add charts, auth, or schedule UI require a new ADR.

## Explicitly out of scope

- Authentication/authorization
- Chart libraries, technical indicators, scoring, recommendations, predictions
- Order placement/transmission
- Schedule configuration UI
- Second data providers, corrections, intraday data
- NAS deployment

## Related documents

- [../overview.md](../overview.md)
- [0003-phase-2-scheduled-watchlist.md](0003-phase-2-scheduled-watchlist.md)
