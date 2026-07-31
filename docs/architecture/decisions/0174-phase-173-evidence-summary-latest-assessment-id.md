# ADR-0174: Phase 173 Evidence Summary Latest Assessment Id

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary nests the full latest assessment object and separately exposes
``most_recent_labeled_assessment_id``. Operators still dig into
``latest_assessment.id`` to get the absolute newest snapshot id for deep links and
compare against the labeled scan id. A top-level field keeps that id visible without
inventing identifiers.

## Decisions

### 1. API

Add ``latest_assessment_id: int | null`` to ``ResearchEvidenceSummaryResponse`` (+ export).
Copy from ``latest_assessment.id`` when present; otherwise null. Never invent. ``ge=1``
when set. Distinct from ``most_recent_labeled_assessment_id`` (which may differ when the
absolute newest snapshot is still unlabeled).

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near most_recent_labeled_assessment_id
(``data-testid="evidence-latest-assessment-id"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0172-phase-171-evidence-summary-latest-probability-confidence.md](0172-phase-171-evidence-summary-latest-probability-confidence.md)
- [0175-phase-174-nas-live-verify-phase-173.md](0175-phase-174-nas-live-verify-phase-173.md)
