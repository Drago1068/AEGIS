# ADR-0064: Phase 63 One-Click Mixed Filter from Evidence Summary

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 61 added assessment history ``component_source`` filtering; Phase 62 live-verified
``component_source=mixed`` returning 19 AAPL rows matching evidence-summary
``mixed_component_source_assessment_count``. Operators still must find the history dropdown
to audit those rows. A one-click path from the evidence count improves auditability without
changing gates or math.

## Decisions

### 1. Console control

When evidence-summary ``mixed_component_source_assessment_count > 0``, the mixed-count value
is a button that:

1. Sets the assessment history source filter to ``mixed``
2. Reloads history via the existing list path (``componentSource: "mixed"``)
3. Scrolls the assessment history section into view

When the count is 0, the value remains plain text (no affordance).

### 2. Scope boundary

Research-only UX. Reuses Phase 61 filter APIs; no new endpoints, no gate changes, no
assessment/label math changes.

### 3. Out of scope

- Default-on calibration
- Preferring mixed rows in backfill ordering
- Actionable promotion, orders, ACME
- NAS live verify (follow-up ops phase)

## Related documents

- [0062-phase-61-assessment-history-component-source-filter.md](0062-phase-61-assessment-history-component-source-filter.md)
- [0063-phase-62-nas-live-verify-phase-61.md](0063-phase-62-nas-live-verify-phase-61.md)
