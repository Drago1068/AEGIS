# ADR-0218: Phase 217 Evidence Summary Most Recent Labeled Outcome Label Method Version

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes ``most_recent_labeled_outcome_label_method_id``. Operators still dig
into ``most_recent_labeled_outcome_label.label_method_version`` for scan-labeled method version
when the absolute latest assessment is unlabeled. A top-level field keeps that version visible
without inventing values. Distinct from ``latest_outcome_label_method_version`` and assessment/
calibration method versions.

## Decisions

### 1. API

Add ``most_recent_labeled_outcome_label_method_version: int | null`` to
``ResearchEvidenceSummaryResponse`` (+ export). Copy from
``most_recent_labeled_outcome_label.label_method_version`` when present; otherwise null. Never
invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near most recent labeled outcome_label
method_id (``data-testid="evidence-most-recent-labeled-outcome-label-method-version"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0216-phase-215-evidence-summary-most-recent-labeled-outcome-label-method-id.md](0216-phase-215-evidence-summary-most-recent-labeled-outcome-label-method-id.md)
- [0219-phase-218-nas-live-verify-phase-217.md](0219-phase-218-nas-live-verify-phase-217.md)
- [0220-phase-219-evidence-summary-most-recent-labeled-outcome-label-schema-version.md](0220-phase-219-evidence-summary-most-recent-labeled-outcome-label-schema-version.md)
