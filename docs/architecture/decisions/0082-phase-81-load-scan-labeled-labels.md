# ADR-0082: Phase 81 Load Scan-Labeled Outcome Labels

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 79 surfaces ``most_recent_labeled_*`` when the absolute latest assessment is unlabeled
(ADR-0080). Phase 80 live-verified those fields on the NAS (``most_recent_labeled_assessment_id=125``
while latest label keys were none). Operators still need a one-click path to load that
assessment’s outcome-label history into the existing console panel without inventing data.

## Decisions

### 1. Console

When scan-labeled rows are shown (differ from absolute latest), add:

- **Load labels for assessment {id}** — calls existing ``listOutcomeLabels`` for
  ``most_recent_labeled_assessment_id`` and populates the outcome-label history section.

Research-only; no new API; calibration defaults remain off.

### 2. Out of scope

New endpoints, changing ``latest_assessment``, default-on calibration, orders, ACME.

## Related documents

- [0080-phase-79-most-recent-labeled-evidence-summary.md](0080-phase-79-most-recent-labeled-evidence-summary.md)
- [0081-phase-80-nas-live-verify-phase-79.md](0081-phase-80-nas-live-verify-phase-79.md)
