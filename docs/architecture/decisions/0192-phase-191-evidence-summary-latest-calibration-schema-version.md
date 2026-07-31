# ADR-0192: Phase 191 Evidence Summary Latest Calibration Schema Version

- Status: Proposed
- Date: 2026-07-31

## Context

Evidence summary now exposes calibration method id and version at the top level. Operators
still dig into ``latest_calibration.schema_version`` for row schema provenance. A top-level
field keeps that version visible without inventing numbers. Distinct from assessment
``latest_schema_version``.

## Decisions

### 1. API

Add ``latest_calibration_schema_version: int | null`` to ``ResearchEvidenceSummaryResponse``
(+ export). Copy from ``latest_calibration.schema_version`` when present; otherwise null.
``ge=1`` when set. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest calibration method_version
(``data-testid="evidence-latest-calibration-schema-version"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0190-phase-189-evidence-summary-latest-calibration-method-version.md](0190-phase-189-evidence-summary-latest-calibration-method-version.md)
- [0193-phase-192-nas-live-verify-phase-191.md](0193-phase-192-nas-live-verify-phase-191.md)
