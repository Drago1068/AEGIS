# AEGIS 3.0 Backend

FastAPI service for the AEGIS 3.0 decision-support platform. See
[../docs/architecture/overview.md](../docs/architecture/overview.md) for module boundaries and
[../docs/operations/local-development.md](../docs/operations/local-development.md) for setup
and command reference.

Phase 0 established process liveness/readiness endpoints and infrastructure wiring. Phase 1
adds on-demand market data ingestion (Alpha Vantage daily bars) with a validated, append-only
TimescaleDB observation store; see
[../docs/architecture/decisions/0002-phase-1-market-data-ingestion.md](../docs/architecture/decisions/0002-phase-1-market-data-ingestion.md).
No scoring, recommendation, prediction, or trading logic exists in this package.
