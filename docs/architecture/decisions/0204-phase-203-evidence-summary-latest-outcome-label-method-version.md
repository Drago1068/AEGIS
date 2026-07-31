# ADR-0204: Phase 203 Evidence Summary Latest Outcome Label Method Version

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes ``latest_outcome_label_method_id``. Operators still dig into
``latest_outcome_label.label_method_version`` for method revision provenance when the latest
assessment is labeled. A top-level field keeps that identity visible without inventing
values. Distinct from assessment ``latest_method_version`` and calibration
``latest_calibration_method_version``.

## Decisions

### 1. API

Add ``latest_outcome_label_method_version: int | null`` to ``ResearchEvidenceSummaryResponse``
(+ export). Copy from ``latest_outcome_label.label_method_version`` when present; otherwise
null. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest outcome label method_id
(``data-testid="evidence-latest-outcome-label-method-version"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0202-phase-201-evidence-summary-latest-outcome-label-method-id.md](0202-phase-201-evidence-summary-latest-outcome-label-method-id.md)
- [0205-phase-204-nas-live-verify-phase-203.md](0205-phase-204-nas-live-verify-phase-203.md)
