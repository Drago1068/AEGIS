# ADR-0182: Phase 181 Evidence Summary Latest Calibration Computed At

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes ``latest_calibration_id`` and ``latest_calibration_horizon_key``.
Operators still dig into ``latest_calibration.computed_at`` to see when that calibration row
was written. A top-level field keeps calibration provenance visible without inventing
timestamps. Distinct from assessment ``latest_computed_at``.

## Decisions

### 1. API

Add ``latest_calibration_computed_at: datetime | null`` to ``ResearchEvidenceSummaryResponse``
(+ export). Copy from ``latest_calibration.computed_at`` when present; otherwise null. Never
invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest calibration horizon
(``data-testid="evidence-latest-calibration-computed-at"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0180-phase-179-evidence-summary-latest-calibration-horizon-key.md](0180-phase-179-evidence-summary-latest-calibration-horizon-key.md)
- [0183-phase-182-nas-live-verify-phase-181.md](0183-phase-182-nas-live-verify-phase-181.md)
