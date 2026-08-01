# ADR-0280: Phase 279 Evidence-Summary Primary Fetch Fallback

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 275–278 closed ingest API + IngestPanel ``primary_fetch_fallback``. Research
evidence-summary did not show whether the latest stored primary tip bar used compact
fallback, so operators had to re-run ingest (or inspect DB) while reviewing research
diagnostics.

Prefer a fail-closed evidence-summary diagnostic derived from stored primary tip
``raw_payload`` over inventing new tip scalars or further UI modularization.

## Decisions

### 1. Evidence-summary diagnostic

Optional ``latest_primary_fetch_fallback: string | null`` on evidence-summary: read
``aegis_fetch_fallback`` from the current max primary-source stored bar for the symbol
(``list_recent(..., sources=[primary])`` tip); ``full_to_compact`` when present; null
otherwise. Surfaced in the research evidence UI and ``verify.ps1``. Never invent closes;
never change provenance ``source``.

### 2. Out of scope

Inventing closes, silent provenance swaps, orders, changing AV output_size defaults.

## Related documents

- [0279-phase-278-nas-live-verify-phase-277.md](0279-phase-278-nas-live-verify-phase-277.md)
- [0281-phase-280-nas-live-verify-phase-279.md](0281-phase-280-nas-live-verify-phase-279.md)
- [0276-phase-275-ingest-primary-fetch-fallback.md](0276-phase-275-ingest-primary-fetch-fallback.md)
