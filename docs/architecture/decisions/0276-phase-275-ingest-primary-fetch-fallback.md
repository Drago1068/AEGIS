# ADR-0276: Phase 275 Surface Primary Fetch Fallback on Ingest Results (draft)

- Status: Proposed (ready after Phase 274; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 273–274 closed AV full→compact tip catch-up (live primary tip ``2026-07-31``).
Fallback is labeled only in bar ``raw_payload`` / logs; ingest API results do not tell
operators whether the primary fetch used configured ``full`` or compact fallback without
a DB inspect.

Prefer a fail-closed ingest diagnostic scalar over further tip mechanics or UI
modularization.

## Decisions (proposed)

### 1. Ingest diagnostic

Add optional ``primary_fetch_fallback: string | null`` (or equivalent) on ingest symbol
results: ``full_to_compact`` when ADR-0274 compact fallback supplied primary bars; null
otherwise. Never invent closes; never change provenance ``source``.

### 2. Out of scope

Inventing closes, UI modularization, orders, changing output_size defaults.

## Resume (after Phase 274 gate)

```powershell
# Surface primary fetch fallback on ingest results (ADR-0276); tests; commit+push; then Phase 276:
# git archive HEAD → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0275-phase-274-nas-live-verify-phase-273.md](0275-phase-274-nas-live-verify-phase-273.md)
- [0277-phase-276-nas-live-verify-phase-275.md](0277-phase-276-nas-live-verify-phase-275.md)
- [0274-phase-273-primary-tip-catch-up-compact.md](0274-phase-273-primary-tip-catch-up-compact.md)
