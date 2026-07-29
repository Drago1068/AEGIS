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
cookie sessions (Redis + httpOnly cookie); `/health` and `/ready` stay public. Phase 6 adds
authenticated research-only assessment routes under `/research/{symbol}/assessments` (method
`daily_bar_research_v1`, append-only snapshots, fail-closed gates). Phase 8 runs that same
method after successful locked scheduled ingest (and after on-demand ingest when
`AEGIS_RESEARCH_SCHEDULE_AFTER_INGEST_ENABLED` is true), using stored bars only. See
[../docs/architecture/decisions/0002-phase-1-market-data-ingestion.md](../docs/architecture/decisions/0002-phase-1-market-data-ingestion.md),
[../docs/architecture/decisions/0003-phase-2-scheduled-watchlist.md](../docs/architecture/decisions/0003-phase-2-scheduled-watchlist.md),
[../docs/architecture/decisions/0005-phase-4-operator-auth.md](../docs/architecture/decisions/0005-phase-4-operator-auth.md),
[../docs/architecture/decisions/0007-phase-6-research-only-scoring.md](../docs/architecture/decisions/0007-phase-6-research-only-scoring.md),
and
[../docs/architecture/decisions/0009-phase-8-scheduled-research.md](../docs/architecture/decisions/0009-phase-8-scheduled-research.md).
Recommendation, prediction, actionable promotion, and trading logic do not exist in this
package.
