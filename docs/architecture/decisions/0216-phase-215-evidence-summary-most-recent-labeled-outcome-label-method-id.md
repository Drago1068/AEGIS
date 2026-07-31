# ADR-0216: Phase 215 Evidence Summary Most Recent Labeled Outcome Label Method Id

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes ``most_recent_labeled_outcome_label_id``. Operators still dig into
``most_recent_labeled_outcome_label.label_method_id`` for scan-labeled method identity when the
absolute latest assessment is unlabeled. A top-level field keeps that identity visible without
inventing strings. Distinct from ``latest_outcome_label_method_id`` and assessment/calibration
method ids.

## Decisions

### 1. API

Add ``most_recent_labeled_outcome_label_method_id: str | null`` to
``ResearchEvidenceSummaryResponse`` (+ export). Copy from
``most_recent_labeled_outcome_label.label_method_id`` when present; otherwise null. Never
invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near most recent labeled outcome_label id
(``data-testid="evidence-most-recent-labeled-outcome-label-method-id"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0214-phase-213-evidence-summary-most-recent-labeled-outcome-label-id.md](0214-phase-213-evidence-summary-most-recent-labeled-outcome-label-id.md)
- [0217-phase-216-nas-live-verify-phase-215.md](0217-phase-216-nas-live-verify-phase-215.md)
- [0218-phase-217-evidence-summary-most-recent-labeled-outcome-label-method-version.md](0218-phase-217-evidence-summary-most-recent-labeled-outcome-label-method-version.md)
