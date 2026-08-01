# ADR-0280: Phase 279 Evidence-Summary Primary Fetch Fallback (draft)

- Status: Proposed (ready after Phase 278; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 275–278 closed ingest API + IngestPanel ``primary_fetch_fallback``. Research
evidence-summary still does not show whether the latest stored primary tip bar used
compact fallback, so operators must re-run ingest (or inspect DB) while reviewing
research diagnostics.

Prefer a fail-closed evidence-summary diagnostic derived from stored primary tip
``raw_payload`` over inventing new tip scalars or further UI modularization.

## Decisions (proposed)

### 1. Evidence-summary diagnostic

Add optional ``latest_primary_fetch_fallback: string | null`` (name may vary) on
evidence-summary: read ``aegis_fetch_fallback`` from the current max primary-source
stored bar for the symbol; ``full_to_compact`` when present; null otherwise.
Never invent closes; never change provenance ``source``.

### 2. Out of scope

Inventing closes, silent provenance swaps, orders, changing AV output_size defaults.

## Resume (after Phase 278 gate)

```powershell
# Surface latest primary fetch fallback on evidence-summary (ADR-0280); tests; commit+push; then Phase 280:
# git archive HEAD → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0279-phase-278-nas-live-verify-phase-277.md](0279-phase-278-nas-live-verify-phase-277.md)
- [0281-phase-280-nas-live-verify-phase-279.md](0281-phase-280-nas-live-verify-phase-279.md)
- [0276-phase-275-ingest-primary-fetch-fallback.md](0276-phase-275-ingest-primary-fetch-fallback.md)
