# ADR-0080: Phase 79 Most-Recent Labeled Outcome on Evidence Summary

- Status: Accepted
- Date: 2026-07-30

## Context

Evidence-summary binds ``latest_outcome_label`` to the absolute newest assessment. On the
live NAS corpus the newest AAPL snapshot is often unlabeled while older scanned
assessments (including mixed) already have labels, so the console shows
``label_keys=(none)`` despite ``mixed_labeled_assessment_count > 0``. Operators need an
auditable pointer to the newest labeled row in the ≤100 scan without inventing labels or
changing ``latest_assessment`` identity.

## Decisions

### 1. API (research-only)

Add to ``GET .../evidence-summary`` (+ export):

- ``most_recent_labeled_assessment_id`` — newest scanned assessment id with a default-method
  label (null when none)
- ``most_recent_labeled_outcome_label`` — that label payload (null when none)

When the absolute latest is labeled, these mirror ``latest_assessment.id`` /
``latest_outcome_label``. ``latest_*`` semantics are unchanged.

### 2. Console

When scan-labeled differs from absolute latest (or latest labels are null), show the
most-recent labeled assessment id and ``Scan-labeled {horizon}`` rows.

### 3. Out of scope

Default-on calibration, changing ``latest_assessment``, invented labels, orders, ACME.

## Related documents

- [0070-phase-69-mixed-labeled-count-evidence-summary.md](0070-phase-69-mixed-labeled-count-evidence-summary.md)
- [0078-phase-77-horizon-detail-expand.md](0078-phase-77-horizon-detail-expand.md)
