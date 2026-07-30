# ADR-0074: Phase 73 Per-Horizon Readiness Mini-Rows on Evidence Summary

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 71 surfaces aggregate calibration corpus/bucket counts from nested
``calibration_readiness`` on the evidence summary (ADR-0072). Multi-horizon readiness
already returns ``by_horizon`` (ADR-0042 / Phase 41), and the separate readiness panel lists
those rows. Operators still need a glanceable per-horizon status on the evidence summary
without opening the readiness panel. Phases 70 and 72 NAS live verify closed on deploy of
``94cf550``.

## Decisions

### 1. Console

When ``evidenceSummary.calibration_readiness.by_horizon`` is present and non-empty, the
evidence-summary section shows a **Readiness by horizon** mini-list:

- ``{outcome_horizon_key}: {status} (corpus={n}, bucket={m})``

Values come from existing nested readiness fields (no new API contracts). Research-only;
no invented confidence; calibration defaults remain off.

### 2. Out of scope

- New API fields or readiness math
- Default-on calibration or gate changes
- Actionable promotion, recommendations, orders
- ACME / public DNS

## Related documents

- [0072-phase-71-calibration-corpus-callout-evidence-summary.md](0072-phase-71-calibration-corpus-callout-evidence-summary.md)
- [0073-phase-72-nas-live-verify-phase-71.md](0073-phase-72-nas-live-verify-phase-71.md)
- [0042-phase-41-multi-horizon-calibration.md](0042-phase-41-multi-horizon-calibration.md)
