# ADR-0180: Phase 179 Evidence Summary Latest Calibration Horizon Key

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes ``latest_calibration_id``. Operators still dig into
``latest_calibration.outcome_horizon_key`` to see which forward horizon that calibration
row covers. A top-level field keeps horizon provenance visible without inventing keys.

## Decisions

### 1. API

Add ``latest_calibration_horizon_key: str | null`` to ``ResearchEvidenceSummaryResponse``
(+ export). Copy from ``latest_calibration.outcome_horizon_key`` when present; otherwise
null. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest calibration id
(``data-testid="evidence-latest-calibration-horizon-key"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0178-phase-177-evidence-summary-latest-calibration-id.md](0178-phase-177-evidence-summary-latest-calibration-id.md)
- [0181-phase-180-nas-live-verify-phase-179.md](0181-phase-180-nas-live-verify-phase-179.md)
