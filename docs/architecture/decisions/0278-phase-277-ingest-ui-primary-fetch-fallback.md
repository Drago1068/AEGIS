# ADR-0278: Phase 277 Surface Primary Fetch Fallback in Ingest UI

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 275–276 closed ingest API ``primary_fetch_fallback`` (live AAPL
``full_to_compact``). The operator IngestPanel still showed primary tip without the
fallback label, so operators had to read verify/API JSON to know compact ran.

Prefer a fail-closed UI diagnostic column over further tip mechanics or evidence-summary
scalar sprawl.

## Decisions

### 1. Ingest UI diagnostic

- Extended ``IngestionSymbolResult`` in ``api-client`` with optional
  ``primary_fetch_fallback: string | null``.
- ``IngestPanel`` shows a **Primary fallback** column: ``full_to_compact`` when present;
  em-dash otherwise.
- Do not invent closes; research-only / fail-closed posture unchanged; no orders.

### 2. Out of scope

Evidence-summary new fields, inventing closes, calibration default-on, orders.

## Related documents

- [0277-phase-276-nas-live-verify-phase-275.md](0277-phase-276-nas-live-verify-phase-275.md)
- [0279-phase-278-nas-live-verify-phase-277.md](0279-phase-278-nas-live-verify-phase-277.md)
- [0276-phase-275-ingest-primary-fetch-fallback.md](0276-phase-275-ingest-primary-fetch-fallback.md)
