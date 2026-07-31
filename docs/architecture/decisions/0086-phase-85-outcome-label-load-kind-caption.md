# ADR-0086: Phase 85 Outcome-Label Load-Kind Caption

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 83 captions the outcome-label panel with the assessment id it was loaded for
(ADR-0084). Phase 81 can load labels for ``most_recent_labeled_assessment_id``, which may
differ from the absolute latest assessment. Operators need the caption to state whether the
panel was loaded from **latest** or **scan-labeled** (and, when different, the latest id).

## Decisions

### 1. Console

Track ``outcomeLabelHistoryLoadKind`` as ``latest`` | ``scan_labeled`` whenever outcome
labels are loaded. Beside the assessment-id caption show:

- **· latest** for refresh/assess/compute/backfill loads
- **· scan-labeled** for the Phase 81 control; append **(latest is {id})** when that id
  differs from the loaded assessment id

### 2. Out of scope

New API fields, default-on calibration, changing ``latest_assessment``, orders, ACME.

## Related documents

- [0084-phase-83-outcome-label-history-assessment-id.md](0084-phase-83-outcome-label-history-assessment-id.md)
- [0082-phase-81-load-scan-labeled-labels.md](0082-phase-81-load-scan-labeled-labels.md)
