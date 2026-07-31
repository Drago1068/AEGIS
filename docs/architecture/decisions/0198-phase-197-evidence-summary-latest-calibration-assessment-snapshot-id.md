# ADR-0198: Phase 197 Evidence Summary Latest Calibration Assessment Snapshot Id

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes calibration-row confidence at the top level. Operators still dig
into ``latest_calibration.assessment_snapshot_id`` to see which assessment the calibration
row is bound to. A top-level field keeps that foreign key visible without inventing ids.
Distinct from ``latest_assessment_id`` when the absolute newest assessment has no calibration.

## Decisions

### 1. API

Add ``latest_calibration_assessment_snapshot_id: int | null`` to
``ResearchEvidenceSummaryResponse`` (+ export). Copy from
``latest_calibration.assessment_snapshot_id`` when present; otherwise null. ``ge=1`` when set.
Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest calibration probability
confidence (``data-testid="evidence-latest-calibration-assessment-snapshot-id"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0196-phase-195-evidence-summary-latest-calibration-probability-confidence.md](0196-phase-195-evidence-summary-latest-calibration-probability-confidence.md)
- [0199-phase-198-nas-live-verify-phase-197.md](0199-phase-198-nas-live-verify-phase-197.md)
