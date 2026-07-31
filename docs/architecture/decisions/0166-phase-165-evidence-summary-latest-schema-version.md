# ADR-0166: Phase 165 Evidence Summary Latest Schema Version

- Status: Proposed
- Date: 2026-07-31

## Context

Evidence summary now exposes method id/version and lookback window for the latest
assessment. Operators still dig into nested ``latest_assessment.schema_version`` to confirm
which assessment payload schema produced the snapshot. A top-level field keeps schema
provenance visible without inventing versions.

## Decisions

### 1. API

Add ``latest_schema_version: int | null`` to ``ResearchEvidenceSummaryResponse`` (+ export).
Copy from ``latest_assessment.schema_version`` when present; otherwise null. Never invent.
``ge=1`` when set.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near method id/version
(``data-testid="evidence-latest-schema-version"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0164-phase-163-evidence-summary-latest-lookback-start.md](0164-phase-163-evidence-summary-latest-lookback-start.md)
- [0167-phase-166-nas-live-verify-phase-165.md](0167-phase-166-nas-live-verify-phase-165.md)
