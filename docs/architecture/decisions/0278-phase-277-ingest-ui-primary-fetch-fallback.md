# ADR-0278: Phase 277 Surface Primary Fetch Fallback in Ingest UI (draft)

- Status: Proposed (ready after Phase 276; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 275–276 closed ingest API ``primary_fetch_fallback`` (live AAPL
``full_to_compact``). The operator IngestPanel still shows primary tip without the
fallback label, so operators must read verify/API JSON to know compact ran.

Prefer a fail-closed UI diagnostic column over further tip mechanics or evidence-summary
scalar sprawl.

## Decisions (proposed)

### 1. Ingest UI diagnostic

- Extend ``IngestionSymbolResult`` in ``api-client`` with optional
  ``primary_fetch_fallback: string | null``.
- Show a clearly labeled column (or cell) on ``IngestPanel``:
  ``full_to_compact`` when present; em-dash / null otherwise.
- Do not invent closes; do not change research-only / fail-closed posture; no orders.

### 2. Out of scope

Evidence-summary new fields, inventing closes, calibration default-on, orders.

## Resume (after Phase 276 gate)

```powershell
# Surface primary_fetch_fallback on IngestPanel (ADR-0278); frontend tests; commit+push; then Phase 278:
# git archive HEAD → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0277-phase-276-nas-live-verify-phase-275.md](0277-phase-276-nas-live-verify-phase-275.md)
- [0279-phase-278-nas-live-verify-phase-277.md](0279-phase-278-nas-live-verify-phase-277.md)
- [0276-phase-275-ingest-primary-fetch-fallback.md](0276-phase-275-ingest-primary-fetch-fallback.md)
