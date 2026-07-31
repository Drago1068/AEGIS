# ADR-0200: Phase 199 Evidence Summary Latest Outcome Label Computed At

- Status: Proposed
- Date: 2026-07-31

## Context

Calibration-row provenance is now fully lifted to top-level evidence-summary fields through
Phase 197. Operators still dig into ``latest_outcome_label.computed_at`` when the absolute
newest assessment is labeled. A top-level field keeps label provenance visible without
inventing timestamps. Distinct from assessment ``latest_computed_at`` and calibration
``latest_calibration_computed_at``. Null when the latest assessment is unlabeled.

## Decisions

### 1. API

Add ``latest_outcome_label_computed_at: datetime | null`` to
``ResearchEvidenceSummaryResponse`` (+ export). Copy from ``latest_outcome_label.computed_at``
when present; otherwise null. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest outcome label id
(``data-testid="evidence-latest-outcome-label-computed-at"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0198-phase-197-evidence-summary-latest-calibration-assessment-snapshot-id.md](0198-phase-197-evidence-summary-latest-calibration-assessment-snapshot-id.md)
- [0201-phase-200-nas-live-verify-phase-199.md](0201-phase-200-nas-live-verify-phase-199.md)
