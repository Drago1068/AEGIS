# AEGIS 3.0 development brief

This file is the primary orientation document for Claude when working in this
repository. Read it together with `.cursor/rules/aegis-project.mdc` before
planning or changing code.

## Mission

Build AEGIS 3.0 from scratch as a modular, self-hosted market
decision-support platform. Local development and verification take place in
`G:\Development\AEGIS`. Deployment to the UGREEN NAS happens only after the
current phase passes its local acceptance gate.

AEGIS must provide transparent, reproducible analysis. It must not place live
orders or imply certainty unsupported by point-in-time evidence.

## Required working method

1. Inspect the repository and current phase documentation.
2. State the phase objective, acceptance criteria, and files expected to
   change.
3. Implement the smallest complete vertical slice.
4. Run tests, linting, type checks, builds, and security-relevant validation.
5. Update the relevant documentation.
6. Stop at the phase gate and summarize evidence before continuing.

Do not skip phases, silently broaden scope, or enable unfinished capabilities.

## Initial technical direction

- Python 3.12+ backend using FastAPI, SQLAlchemy, Alembic, Pydantic, and pytest.
- PostgreSQL with TimescaleDB for versioned time-series observations.
- Redis for bounded caching and background coordination where justified.
- Next.js with TypeScript and Tailwind CSS for the web application.
- Docker Compose for local integration and UGREEN NAS packaging.
- Provider adapters, domain services, persistence, API contracts, and UI
  components must remain clearly separated.

These defaults may be changed only through a documented architecture decision.

## First development task

Start with Phase 0: repository and architecture foundation. Propose a concise
phase plan and acceptance checklist before scaffolding application code. Phase
0 should establish:

- documented architecture and domain boundaries;
- backend and frontend package/tooling choices;
- configuration and secret-handling conventions;
- local Docker Compose topology;
- test, lint, type-check, and build commands;
- CI validation;
- a deployment boundary that keeps NAS work disabled until local acceptance.

Do not implement scoring, recommendations, predictions, or trading logic in
Phase 0.
