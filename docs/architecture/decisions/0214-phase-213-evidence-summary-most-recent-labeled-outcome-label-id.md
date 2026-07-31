# ADR-0214: Phase 213 Evidence Summary Most Recent Labeled Outcome Label Id

- Status: Accepted
- Date: 2026-07-31

## Context

Absolute-latest ``latest_outcome_label_*`` scalars are complete (Phases 175–212). Live NAS
verify repeatedly shows AAPL ``latest_outcome_label_id=null`` while
``most_recent_labeled_assessment_id`` is non-null. Operators and export/NAS checks still dig
into nested ``most_recent_labeled_outcome_label.id`` for the scan-labeled label-row identity.
A top-level field keeps that id visible without inventing values.

## Decisions

### 1. API

Add ``most_recent_labeled_outcome_label_id: int | null`` to ``ResearchEvidenceSummaryResponse``
(+ export). Copy from ``most_recent_labeled_outcome_label.id`` when present; otherwise null.
Distinct from ``latest_outcome_label_id`` and ``most_recent_labeled_assessment_id``. Never
invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest outcome_label id
(``data-testid="evidence-most-recent-labeled-outcome-label-id"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts,
``latest_outcome_label_assessment_snapshot_id`` (redundant with ``latest_assessment_id``).

## Related documents

- [0213-phase-212-nas-live-verify-phase-211.md](0213-phase-212-nas-live-verify-phase-211.md)
- [0215-phase-214-nas-live-verify-phase-213.md](0215-phase-214-nas-live-verify-phase-213.md)
- [0216-phase-215-evidence-summary-most-recent-labeled-outcome-label-method-id.md](0216-phase-215-evidence-summary-most-recent-labeled-outcome-label-method-id.md)
