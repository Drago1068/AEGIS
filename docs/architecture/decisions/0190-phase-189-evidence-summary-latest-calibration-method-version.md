# ADR-0190: Phase 189 Evidence Summary Latest Calibration Method Version

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes ``latest_calibration_method_id``. Operators still dig into
``latest_calibration.calibration_method_version`` for method version provenance. A top-level
field keeps that version visible without inventing numbers. Distinct from assessment
``latest_method_version``.

## Decisions

### 1. API

Add ``latest_calibration_method_version: int | null`` to ``ResearchEvidenceSummaryResponse``
(+ export). Copy from ``latest_calibration.calibration_method_version`` when present;
otherwise null. ``ge=1`` when set. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest calibration method_id
(``data-testid="evidence-latest-calibration-method-version"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0188-phase-187-evidence-summary-latest-calibration-method-id.md](0188-phase-187-evidence-summary-latest-calibration-method-id.md)
- [0191-phase-190-nas-live-verify-phase-189.md](0191-phase-190-nas-live-verify-phase-189.md)
