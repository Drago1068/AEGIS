# AEGIS 3.0 Backend

FastAPI service for the AEGIS 3.0 decision-support platform. See
[../docs/architecture/overview.md](../docs/architecture/overview.md) for module boundaries and
[../docs/operations/local-development.md](../docs/operations/local-development.md) for setup
and command reference.

Phase 0 established process liveness/readiness endpoints and infrastructure wiring. Phase 1
added on-demand market data ingestion (Alpha Vantage daily bars) with a validated, append-only
TimescaleDB observation store. Phase 2 adds an in-process scheduler that runs ingestion
automatically (guarded by a Redis lock) and a database-backed watchlist manageable via
`GET/POST /watchlist` and `DELETE /watchlist/{symbol}`. Phase 4 protects those routes with
cookie sessions (Redis + httpOnly cookie); `/health` and `/ready` stay public. See
[../docs/architecture/decisions/0002-phase-1-market-data-ingestion.md](../docs/architecture/decisions/0002-phase-1-market-data-ingestion.md),
[../docs/architecture/decisions/0003-phase-2-scheduled-watchlist.md](../docs/architecture/decisions/0003-phase-2-scheduled-watchlist.md),
and
[../docs/architecture/decisions/0005-phase-4-operator-auth.md](../docs/architecture/decisions/0005-phase-4-operator-auth.md).
No scoring, recommendation, prediction, or trading logic exists in this package.
