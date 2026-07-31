# ADR-0206: Phase 205 Evidence Summary Latest Outcome Label Schema Version

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes ``latest_outcome_label_method_version``. Operators still dig into
``latest_outcome_label.schema_version`` for label schema provenance when the latest assessment
is labeled. A top-level field keeps that identity visible without inventing values. Distinct
from assessment ``latest_schema_version`` and calibration ``latest_calibration_schema_version``.

## Decisions

### 1. API

Add ``latest_outcome_label_schema_version: int | null`` to ``ResearchEvidenceSummaryResponse``
(+ export). Copy from ``latest_outcome_label.schema_version`` when present; otherwise null.
Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest outcome label method_version
(``data-testid="evidence-latest-outcome-label-schema-version"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0204-phase-203-evidence-summary-latest-outcome-label-method-version.md](0204-phase-203-evidence-summary-latest-outcome-label-method-version.md)
- [0207-phase-206-nas-live-verify-phase-205.md](0207-phase-206-nas-live-verify-phase-205.md)
