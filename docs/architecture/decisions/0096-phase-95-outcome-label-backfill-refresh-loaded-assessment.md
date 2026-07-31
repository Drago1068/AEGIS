# ADR-0096: Phase 95 Outcome-Label Backfill Refresh Uses Loaded Assessment Id

- Status: Accepted (draft / pending implementation)
- Date: 2026-07-30

## Context

Phases 87–93 bind download and compute to ``outcomeLabelHistoryAssessmentId`` when set.
``onBackfillOutcomeLabels`` still refreshes label history only for ``latest.id``, so after
backfill the panel can snap away from a scan-labeled assessment the operator was viewing.

## Decisions

### 1. Console

After a successful outcome-label backfill, reload outcome-label history for
``outcomeLabelHistoryAssessmentId ?? latest.id`` (when either is set), preserving
load-kind when the history assessment id was already tracked.

### 2. Out of scope

New API fields, default-on calibration, changing ``latest_assessment``, orders, ACME.

## Resume

Implement UI + unit tests; update CHANGELOG/README/overview; then Phase 96 NAS verify.

## Related documents

- [0094-phase-93-compute-outcome-labels-loaded-assessment.md](0094-phase-93-compute-outcome-labels-loaded-assessment.md)
- [0088-phase-87-outcome-label-download-loaded-assessment.md](0088-phase-87-outcome-label-download-loaded-assessment.md)
