# ADR-0098: Phase 97 Assessment Backfill Preserves Loaded Outcome Labels

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 95 preserves the loaded outcome-label assessment after outcome-label backfill.
``onBackfillAssessments`` still reloads outcome labels for the new ``latest.id``, snapping
the panel away from a scan-labeled assessment the operator was viewing.

## Decisions

### 1. Console

After assessment backfill, update ``latest`` as today. Reload outcome-label history for
``outcomeLabelHistoryAssessmentId ?? nextLatest.id`` (when either is set), preserving
load-kind when a history assessment id was already tracked. Calibration history still
loads for ``nextLatest.id``.

### 2. Out of scope

New API fields, default-on calibration, changing assessment selection UX beyond refresh,
orders, ACME.

## Related documents

- [0096-phase-95-outcome-label-backfill-refresh-loaded-assessment.md](0096-phase-95-outcome-label-backfill-refresh-loaded-assessment.md)
- [0094-phase-93-compute-outcome-labels-loaded-assessment.md](0094-phase-93-compute-outcome-labels-loaded-assessment.md)
