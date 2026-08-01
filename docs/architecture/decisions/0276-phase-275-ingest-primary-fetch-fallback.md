# ADR-0276: Phase 275 Surface Primary Fetch Fallback on Ingest Results

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 273–274 closed AV full→compact tip catch-up (live primary tip ``2026-07-31``).
Fallback was labeled only in bar ``raw_payload`` / logs; ingest API results did not tell
operators whether the primary fetch used configured ``full`` or compact fallback without
a DB inspect.

Prefer a fail-closed ingest diagnostic scalar over further tip mechanics or UI
modularization.

## Decisions

### 1. Ingest diagnostic

Optional ``primary_fetch_fallback: string | null`` on ingest symbol results:
``full_to_compact`` when ADR-0274 compact fallback supplied primary bars (read from
``raw_payload["aegis_fetch_fallback"]`` on primary-source bars); null otherwise.
Never invent closes; never change provenance ``source``. Secondary-only writes leave
the field null even if secondary bars carry unrelated labels.

### 2. Out of scope

Inventing closes, UI modularization, orders, changing output_size defaults.

## Related documents

- [0275-phase-274-nas-live-verify-phase-273.md](0275-phase-274-nas-live-verify-phase-273.md)
- [0277-phase-276-nas-live-verify-phase-275.md](0277-phase-276-nas-live-verify-phase-275.md)
- [0274-phase-273-primary-tip-catch-up-compact.md](0274-phase-273-primary-tip-catch-up-compact.md)
