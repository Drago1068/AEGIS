# ADR-0196: Phase 195 Evidence Summary Latest Calibration Probability Confidence

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes calibration state at the top level. Operators still dig into
``latest_calibration.probability_confidence`` for the calibration-row confidence. A top-level
field keeps that value visible without inventing probabilities. Distinct from assessment
``latest_probability_confidence`` (which may be set when a calibration is attached to the
assessment snapshot).

## Decisions

### 1. API

Add ``latest_calibration_probability_confidence: float | null`` to
``ResearchEvidenceSummaryResponse`` (+ export). Copy from
``latest_calibration.probability_confidence`` when present; otherwise null. ``ge=0``, ``le=1``
when set. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest calibration state
(``data-testid="evidence-latest-calibration-probability-confidence"``), labeled to
disambiguate from assessment probability confidence.

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0194-phase-193-evidence-summary-latest-calibration-state.md](0194-phase-193-evidence-summary-latest-calibration-state.md)
- [0197-phase-196-nas-live-verify-phase-195.md](0197-phase-196-nas-live-verify-phase-195.md)
