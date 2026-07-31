# ADR-0092: Phase 91 Outcome-Label Empty State for Loaded Assessment

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 81–89 can load outcome labels for a specific assessment id (including scan-labeled).
When ``listOutcomeLabels`` returns ``[]``, ``outcomeLabel`` stays null and the outcome-label
panel (including assessment-id / load-kind captions) is hidden, so operators lose the audit
context that a load was attempted for that id.

## Decisions

### 1. Console

When ``outcomeLabelHistoryAssessmentId`` is set and there is no ``outcomeLabel`` row to
display, still render the outcome-label panel shell with:

- The existing assessment-id / load-kind captions
- An empty-state line: **No outcome labels stored for assessment {id}** (research-only;
  do not invent values)

### 2. Out of scope

New API fields, default-on calibration, changing ``latest_assessment``, orders, ACME.

## Related documents

- [0084-phase-83-outcome-label-history-assessment-id.md](0084-phase-83-outcome-label-history-assessment-id.md)
- [0090-phase-89-outcome-label-download-names-assessment.md](0090-phase-89-outcome-label-download-names-assessment.md)
- [0093-phase-92-nas-live-verify-phase-91.md](0093-phase-92-nas-live-verify-phase-91.md)
