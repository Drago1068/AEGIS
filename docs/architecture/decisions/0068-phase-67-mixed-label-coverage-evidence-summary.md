# ADR-0068: Phase 67 Mixed Label Coverage on Evidence Summary

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 66 live-verified prefer-mixed outcome-label backfill and labeled 19 AAPL mixed
assessments in one pass. Operators need evidence-summary fields that show how many scanned
mixed assessments still lack labels and which ``bar_source`` the newest labeled mixed row
used — without opening each assessment.

## Decisions

### 1. Evidence-summary fields

``GET /research/{symbol}/evidence-summary`` (and export) add:

- ``mixed_unlabeled_assessment_count`` — among newest ≤100 assessments with
  ``component_source=mixed``, count those without a default-method outcome label
- ``latest_mixed_label_bar_source`` — ``bar_source`` from the newest mixed assessment that
  has a persisted label; null when none of the scanned mixed rows are labeled

Existing ``mixed_component_source_assessment_count`` is unchanged. Missing pieces remain
null or zero. No invented confidence or labels.

### 2. Console

Research console evidence-summary section surfaces both fields next to the mixed count.

### 3. Out of scope

- Changing assessment/label math or fail-closed gates
- Default-on calibration
- Actionable promotion, orders, ACME
- NAS live verify (follow-up ops phase)

## Related documents

- [0060-phase-59-cross-source-provenance-evidence-summary.md](0060-phase-59-cross-source-provenance-evidence-summary.md)
- [0066-phase-65-prefer-mixed-label-backfill.md](0066-phase-65-prefer-mixed-label-backfill.md)
- [0067-phase-66-nas-live-verify-phase-65.md](0067-phase-66-nas-live-verify-phase-65.md)
