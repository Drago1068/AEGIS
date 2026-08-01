# ADR-0282: Phase 281 Daily-Bars Tip Fetch Fallback (draft)

- Status: Proposed (ready after Phase 280; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 275–280 closed primary fetch-fallback diagnostics on ingest results,
IngestPanel, and evidence-summary (live AAPL ``full_to_compact``). The symbol
daily-bars read API still omits the tip bar's ``aegis_fetch_fallback``, so the
bars page cannot show compact provenance without opening research evidence.

Prefer a fail-closed optional field on daily-bar responses derived from stored
``raw_payload`` over inventing further tip scalars or recommendation logic.

## Decisions (proposed)

### 1. Daily-bars diagnostic

Add optional ``fetch_fallback: string | null`` on ``DailyBarResponse`` (or
equivalent): read ``aegis_fetch_fallback`` from that observation's
``raw_payload``; never expose unrelated raw provider secrets. Null when absent.
Never invent closes; never change provenance ``source``.

### 2. Out of scope

Orders, recommendation/actionable promotion, changing AV output_size defaults,
evidence-summary further tip scalars.

## Resume (after Phase 280 gate)

```powershell
# Surface fetch_fallback on daily-bars responses (ADR-0282); tests; commit+push; then Phase 282:
# git archive HEAD → NAS; rebuild backend(+frontend if UI) TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0281-phase-280-nas-live-verify-phase-279.md](0281-phase-280-nas-live-verify-phase-279.md)
- [0283-phase-282-nas-live-verify-phase-281.md](0283-phase-282-nas-live-verify-phase-281.md)
- [0280-phase-279-evidence-summary-primary-fetch-fallback.md](0280-phase-279-evidence-summary-primary-fetch-fallback.md)
