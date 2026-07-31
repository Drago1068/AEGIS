# ADR-0168: Phase 167 Evidence Summary Latest Computed At

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes method, lookback, and schema provenance for the latest
assessment. Operators still dig into nested ``latest_assessment.computed_at`` to confirm
when the snapshot was produced. A top-level field keeps computation freshness visible
without inventing timestamps.

## Decisions

### 1. API

Add ``latest_computed_at: datetime | null`` to ``ResearchEvidenceSummaryResponse`` (+ export).
Copy from ``latest_assessment.computed_at`` when present; otherwise null. Never invent.
JSON serialization remains ISO-8601.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near schema_version
(``data-testid="evidence-latest-computed-at"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0166-phase-165-evidence-summary-latest-schema-version.md](0166-phase-165-evidence-summary-latest-schema-version.md)
- [0169-phase-168-nas-live-verify-phase-167.md](0169-phase-168-nas-live-verify-phase-167.md)
