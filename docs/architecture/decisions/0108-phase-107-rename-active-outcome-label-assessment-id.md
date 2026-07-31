# ADR-0108: Phase 107 Rename Active Outcome-Label Assessment Id Helper

- Status: Accepted (draft / pending implementation)
- Date: 2026-07-30

## Context

Phases 87–105 reuse ``downloadOutcomeLabelsAssessmentId`` for compute, download, and
related outcome-label actions. The name implies download-only and makes later audits harder.

## Decisions

### 1. Console

Rename the shared derived id to ``activeOutcomeLabelAssessmentId``
(``outcomeLabelHistoryAssessmentId ?? latest?.id ?? null``). Update button disable/aria
bindings and tests accordingly. No behavior change.

### 2. Out of scope

New API fields, UX copy changes beyond the rename, default-on calibration, orders, ACME.

## Resume

Implement rename + unit tests; update CHANGELOG/README/overview; then Phase 108 NAS verify.

## Related documents

- [0088-phase-87-outcome-label-download-loaded-assessment.md](0088-phase-87-outcome-label-download-loaded-assessment.md)
- [0094-phase-93-compute-outcome-labels-loaded-assessment.md](0094-phase-93-compute-outcome-labels-loaded-assessment.md)
