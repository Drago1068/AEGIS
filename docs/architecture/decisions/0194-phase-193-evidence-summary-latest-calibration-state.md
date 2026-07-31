# ADR-0194: Phase 193 Evidence Summary Latest Calibration State

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes calibration schema version at the top level. Operators still dig
into ``latest_calibration.state`` to confirm the calibration row remains research-only. A
top-level field keeps that fail-closed state visible without inventing labels.

## Decisions

### 1. API

Add ``latest_calibration_state: str | null`` to ``ResearchEvidenceSummaryResponse`` (+ export).
Copy from ``latest_calibration.state`` when present; otherwise null. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest calibration schema_version
(``data-testid="evidence-latest-calibration-state"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0192-phase-191-evidence-summary-latest-calibration-schema-version.md](0192-phase-191-evidence-summary-latest-calibration-schema-version.md)
- [0195-phase-194-nas-live-verify-phase-193.md](0195-phase-194-nas-live-verify-phase-193.md)
