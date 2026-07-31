# ADR-0222: Phase 221 Evidence Summary Most Recent Labeled Outcome Label State

- Status: Proposed (pending implementation after Phase 220)
- Date: 2026-07-31

## Context

Evidence summary will expose scan-labeled ``most_recent_labeled_outcome_label_schema_version``.
Operators still dig into ``most_recent_labeled_outcome_label.state`` when the absolute latest
assessment is unlabeled. A top-level field keeps that state visible without inventing values.
Distinct from ``latest_outcome_label_state`` and assessment/calibration states.

## Decisions

### 1. API

Add ``most_recent_labeled_outcome_label_state: str | null`` to
``ResearchEvidenceSummaryResponse`` (+ export). Copy from
``most_recent_labeled_outcome_label.state`` when present; otherwise null. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near most recent labeled schema_version
(``data-testid="evidence-most-recent-labeled-outcome-label-state"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0220-phase-219-evidence-summary-most-recent-labeled-outcome-label-schema-version.md](0220-phase-219-evidence-summary-most-recent-labeled-outcome-label-schema-version.md)
- [0223-phase-222-nas-live-verify-phase-221.md](0223-phase-222-nas-live-verify-phase-221.md)
