# ADR-0262: Phase 261 Provider Tip Ahead of Store Tip (draft)

- Status: Proposed (ready after Phase 260; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 259–260 exposed ingest ``latest_trading_date``. Live AAPL showed provider tip
``2026-07-30`` while store / evidence tip stayed ``2026-07-29`` with ``stored=0`` and
``skipped_existing=501``. Operators can now see divergence; the product gap is
**explaining and closing** why a newer provider close does not advance
``latest_assessment_last_available_label_bar_date`` / calendar lag.

Prefer a fail-closed root-cause fix (validation, source selection, or persist path) over
another tip scalar or UI modularization.

## Decisions (proposed)

### 1. Investigate and fix

1. Reproduce with AAPL ingest + bar inspect: confirm whether ``2026-07-30`` exists for the
   resolved label source, was rejected, or was written under a different ``source``.
2. Implement the smallest fail-closed fix so a successful provider tip at or after store tip
   either persists into the label source or is explicitly counted/rejected with a clear
   reason (never invent closes).
3. Extend verify logging only if needed to show rejection reason for the provider tip date.

### 2. Out of scope

New evidence-summary fields, inventing closes, default-on calibration, orders, UI
modularization.

### 3. Why this next

Provider tip ahead of store tip is the blocker for tip advancement; diagnostics already
prove the gap.

## Resume (after Phase 260 gate)

```powershell
# Investigate provider tip 2026-07-30 vs store tip 2026-07-29 (ADR-0262); fix; tests; commit+push; then Phase 262:
# git archive HEAD → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0260-phase-259-ingest-run-latest-trading-date.md](0260-phase-259-ingest-run-latest-trading-date.md)
- [0261-phase-260-nas-live-verify-phase-259.md](0261-phase-260-nas-live-verify-phase-259.md)
- [0263-phase-262-nas-live-verify-phase-261.md](0263-phase-262-nas-live-verify-phase-261.md)
- [0013-phase-12-provider-historical-corrections.md](0013-phase-12-provider-historical-corrections.md)
