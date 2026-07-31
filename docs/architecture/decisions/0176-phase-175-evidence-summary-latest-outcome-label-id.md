# ADR-0176: Phase 175 Evidence Summary Latest Outcome Label Id

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary nests ``latest_outcome_label`` and exposes assessment ids at the top level.
Operators still dig into ``latest_outcome_label.id`` for deep links when the absolute newest
assessment is labeled. A top-level field keeps that id visible without inventing identifiers.

## Decisions

### 1. API

Add ``latest_outcome_label_id: int | null`` to ``ResearchEvidenceSummaryResponse`` (+ export).
Copy from ``latest_outcome_label.id`` when present; otherwise null. Never invent. ``ge=1``
when set. Null when the latest assessment is unlabeled (even if
``most_recent_labeled_outcome_label`` is set).

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest assessment id
(``data-testid="evidence-latest-outcome-label-id"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0174-phase-173-evidence-summary-latest-assessment-id.md](0174-phase-173-evidence-summary-latest-assessment-id.md)
- [0177-phase-176-nas-live-verify-phase-175.md](0177-phase-176-nas-live-verify-phase-175.md)
