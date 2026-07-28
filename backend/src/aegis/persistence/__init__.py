"""Direct database and cache access.

This package owns all direct access to PostgreSQL/TimescaleDB (via SQLAlchemy, with schema
managed by Alembic in ``backend/alembic/``) and Redis. It enforces the append-only,
versioned, timestamped, provenance-aware storage conventions described in
``docs/architecture/data-model.md``. Domain code never opens a database or cache connection
directly; it depends on repository interfaces defined here.

Phase 0 note: this package contains only infrastructure wiring (engine/client construction
and health checks). No domain tables or repositories exist yet.
"""
