# ADR-0084: Phase 83 Outcome-Label History Assessment Id Caption

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 81 loads outcome labels for ``most_recent_labeled_assessment_id`` (ADR-0082), which
may differ from the absolute latest assessment. Phase 82 live-verified the frontend
redeploy. Operators need a clear caption stating which assessment id the currently shown
outcome-label panel was loaded for, so scan-labeled loads are auditable.

## Decisions

### 1. Console

Track ``outcomeLabelHistoryAssessmentId`` whenever outcome labels are loaded. When the
outcome-label panel is visible, show:

- **Assessment id {n}** under the panel title (research-only; no invented data)

### 2. Out of scope

New API fields, default-on calibration, changing ``latest_assessment``, orders, ACME.

## Related documents

- [0082-phase-81-load-scan-labeled-labels.md](0082-phase-81-load-scan-labeled-labels.md)
- [0083-phase-82-nas-live-verify-phase-81.md](0083-phase-82-nas-live-verify-phase-81.md)
