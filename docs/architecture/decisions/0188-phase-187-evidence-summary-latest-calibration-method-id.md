# ADR-0188: Phase 187 Evidence Summary Latest Calibration Method Id

- Status: Proposed
- Date: 2026-07-31

## Context

Evidence summary now exposes calibration corpus and bucket counts at the top level. Operators
still dig into ``latest_calibration.calibration_method_id`` for method provenance on that
row. A top-level field keeps method identity visible without inventing strings. Distinct from
assessment ``latest_method_id``.

## Decisions

### 1. API

Add ``latest_calibration_method_id: str | null`` to ``ResearchEvidenceSummaryResponse``
(+ export). Copy from ``latest_calibration.calibration_method_id`` when present; otherwise
null. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest calibration bucket_count
(``data-testid="evidence-latest-calibration-method-id"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0186-phase-185-evidence-summary-latest-calibration-bucket-count.md](0186-phase-185-evidence-summary-latest-calibration-bucket-count.md)
- [0189-phase-188-nas-live-verify-phase-187.md](0189-phase-188-nas-live-verify-phase-187.md)
