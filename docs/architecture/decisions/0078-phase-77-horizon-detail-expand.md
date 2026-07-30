# ADR-0078: Phase 77 Evidence-Summary Horizon Detail Expand

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 73 added readiness-by-horizon mini-rows on the evidence summary (ADR-0074). Operators
see status/corpus/bucket at a glance but must open the separate readiness panel to read the
fail-closed ``detail`` string. Nested ``by_horizon.detail`` is already on the evidence-summary
payload (no new API).

## Decisions

### 1. Console

Evidence-summary horizon mini-rows are clickable toggles:

- Collapsed: ``{horizon}: {status} (corpus=n, bucket=m)``
- Expanded: show nested ``detail`` under the row (research-only; empty detail shows
  ``(no detail)``)
- One row expanded at a time; refresh evidence summary clears expansion

### 2. Out of scope

- New API fields or readiness math
- Default-on calibration
- Actionable promotion, recommendations, orders
- ACME / public DNS

## Related documents

- [0074-phase-73-per-horizon-readiness-evidence-summary.md](0074-phase-73-per-horizon-readiness-evidence-summary.md)
- [0076-phase-75-evidence-summary-by-horizon-verify.md](0076-phase-75-evidence-summary-by-horizon-verify.md)
