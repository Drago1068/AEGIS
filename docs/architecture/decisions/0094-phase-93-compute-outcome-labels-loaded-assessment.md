# ADR-0094: Phase 93 Compute Outcome Labels Uses Loaded Assessment Id

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 91 shows an empty-state when a loaded assessment has no labels. ``Compute outcome
labels`` still targeted ``latest.id``, so operators viewing a scan-labeled empty panel
could compute labels for the wrong assessment.

## Decisions

### 1. Console

When computing outcome labels, use ``outcomeLabelHistoryAssessmentId`` when set; else
``latest.id``. After compute, reload history for that id preserving load-kind. The compute
control shows ``({id})`` and an accessible name including the assessment id (mirrors
Phase 89 download naming).

### 2. Out of scope

New API fields, default-on calibration, changing ``latest_assessment``, orders, ACME.

## Related documents

- [0092-phase-91-outcome-label-empty-state-loaded-assessment.md](0092-phase-91-outcome-label-empty-state-loaded-assessment.md)
- [0088-phase-87-outcome-label-download-loaded-assessment.md](0088-phase-87-outcome-label-download-loaded-assessment.md)
