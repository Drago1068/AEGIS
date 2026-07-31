# ADR-0088: Phase 87 Outcome-Label Download Uses Loaded Assessment Id

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 81–85 can show outcome labels for ``most_recent_labeled_assessment_id`` while
``latest_assessment.id`` differs. ``onDownloadOutcomeLabels`` still exports via
``latest.id``, so operators can download labels that do not match the panel caption.

## Decisions

### 1. Console

When downloading outcome-label JSON, use ``outcomeLabelHistoryAssessmentId`` when set
(the assessment the panel was loaded for). Fall back to ``latest.id`` only when no
history assessment id is tracked. Keep research-only labeling; do not invent rows.

### 2. Out of scope

New API fields, default-on calibration, changing ``latest_assessment``, orders, ACME.

## Related documents

- [0086-phase-85-outcome-label-load-kind-caption.md](0086-phase-85-outcome-label-load-kind-caption.md)
- [0084-phase-83-outcome-label-history-assessment-id.md](0084-phase-83-outcome-label-history-assessment-id.md)
- [0089-phase-88-nas-live-verify-phase-87.md](0089-phase-88-nas-live-verify-phase-87.md)
