# ADR-0202: Phase 201 Evidence Summary Latest Outcome Label Method Id

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes ``latest_outcome_label_computed_at``. Operators still dig into
``latest_outcome_label.label_method_id`` for method provenance when the latest assessment is
labeled. A top-level field keeps that identity visible without inventing strings. Distinct
from assessment ``latest_method_id`` and calibration ``latest_calibration_method_id``.

## Decisions

### 1. API

Add ``latest_outcome_label_method_id: str | null`` to ``ResearchEvidenceSummaryResponse``
(+ export). Copy from ``latest_outcome_label.label_method_id`` when present; otherwise null.
Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest outcome label computed_at
(``data-testid="evidence-latest-outcome-label-method-id"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0200-phase-199-evidence-summary-latest-outcome-label-computed-at.md](0200-phase-199-evidence-summary-latest-outcome-label-computed-at.md)
- [0203-phase-202-nas-live-verify-phase-201.md](0203-phase-202-nas-live-verify-phase-201.md)
