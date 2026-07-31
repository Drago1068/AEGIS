# ADR-0106: Phase 105 Load Labels for Latest Assessment

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 81 loads outcome labels for ``most_recent_labeled_assessment_id``. Phase 103 notes
that calibration still uses ``latest`` when those differ. Operators need a one-click return
to labels for ``latest.id`` without refreshing the whole latest snapshot.

## Decisions

### 1. Console

When ``outcomeLabelHistoryAssessmentId`` is set and differs from ``latest.id``, show:

- **Load labels for latest {id}** (``data-testid="load-latest-labels"``)

Clicking loads outcome-label history for ``latest.id`` with load-kind ``latest``.

### 2. Out of scope

New API fields, default-on calibration, changing ``latest_assessment``, orders, ACME.

## Related documents

- [0104-phase-103-calibration-controls-note-scan-labeled.md](0104-phase-103-calibration-controls-note-scan-labeled.md)
- [0082-phase-81-load-scan-labeled-labels.md](0082-phase-81-load-scan-labeled-labels.md)
