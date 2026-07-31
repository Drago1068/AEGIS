# ADR-0178: Phase 177 Evidence Summary Latest Calibration Id

- Status: Proposed
- Date: 2026-07-31

## Context

Evidence summary nests ``latest_calibration`` and now exposes assessment and outcome-label
ids at the top level. Operators still dig into ``latest_calibration.id`` for deep links when
a calibration row is attached to the latest assessment. A top-level field keeps that id
visible without inventing identifiers.

## Decisions

### 1. API

Add ``latest_calibration_id: int | null`` to ``ResearchEvidenceSummaryResponse`` (+ export).
Copy from ``latest_calibration.id`` when present; otherwise null. Never invent. ``ge=1``
when set.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest outcome label id
(``data-testid="evidence-latest-calibration-id"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0176-phase-175-evidence-summary-latest-outcome-label-id.md](0176-phase-175-evidence-summary-latest-outcome-label-id.md)
- [0179-phase-178-nas-live-verify-phase-177.md](0179-phase-178-nas-live-verify-phase-177.md)
