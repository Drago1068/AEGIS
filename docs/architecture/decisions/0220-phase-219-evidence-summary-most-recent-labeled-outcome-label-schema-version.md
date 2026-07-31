# ADR-0220: Phase 219 Evidence Summary Most Recent Labeled Outcome Label Schema Version

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes scan-labeled ``most_recent_labeled_outcome_label_id``,
``_method_id``, and ``_method_version``. Operators still dig into
``most_recent_labeled_outcome_label.schema_version`` when the absolute latest assessment is
unlabeled. A top-level field keeps that schema version visible without inventing values.
Distinct from ``latest_outcome_label_schema_version`` and assessment/calibration schema
versions.

## Decisions

### 1. API

Add ``most_recent_labeled_outcome_label_schema_version: int | null`` to
``ResearchEvidenceSummaryResponse`` (+ export). Copy from
``most_recent_labeled_outcome_label.schema_version`` when present; otherwise null. Never
invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near most recent labeled method_version
(``data-testid="evidence-most-recent-labeled-outcome-label-schema-version"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0218-phase-217-evidence-summary-most-recent-labeled-outcome-label-method-version.md](0218-phase-217-evidence-summary-most-recent-labeled-outcome-label-method-version.md)
- [0221-phase-220-nas-live-verify-phase-219.md](0221-phase-220-nas-live-verify-phase-219.md)
- [0222-phase-221-evidence-summary-most-recent-labeled-outcome-label-state.md](0222-phase-221-evidence-summary-most-recent-labeled-outcome-label-state.md)
