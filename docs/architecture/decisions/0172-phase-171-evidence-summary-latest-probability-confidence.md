# ADR-0172: Phase 171 Evidence Summary Latest Probability Confidence

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary already surfaces ``latest_coverage_confidence`` separately from probability
confidence. Operators still dig into nested ``latest_assessment.probability_confidence`` to
see whether a calibrated probability is attached to the latest snapshot. A top-level field
keeps that distinction visible without inventing confidence.

## Decisions

### 1. API

Add ``latest_probability_confidence: float | null`` to ``ResearchEvidenceSummaryResponse``
(+ export). Copy from ``latest_assessment.probability_confidence`` when present; otherwise
null. Never invent. When set, ``ge=0.0`` and ``le=1.0``. Distinct from
``latest_coverage_confidence``.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near coverage_confidence
(``data-testid="evidence-latest-probability-confidence"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts, actionable
promotion.

## Related documents

- [0148-phase-147-evidence-summary-latest-coverage-confidence.md](0148-phase-147-evidence-summary-latest-coverage-confidence.md)
- [0173-phase-172-nas-live-verify-phase-171.md](0173-phase-172-nas-live-verify-phase-171.md)
