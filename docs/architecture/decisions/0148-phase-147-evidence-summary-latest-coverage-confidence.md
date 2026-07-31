# ADR-0148: Phase 147 Evidence Summary Latest Coverage Confidence

- Status: Proposed
- Date: 2026-07-30

## Context

Evidence summary already nests the latest assessment (including ``coverage_confidence``)
and surfaces ``latest_calibration.probability_confidence``. Operators benefit from an
explicit top-level ``latest_coverage_confidence`` so coverage stays visibly separate from
probability confidence without digging into nested assessment JSON.

## Decisions

### 1. API

Add ``latest_coverage_confidence: float | null`` to ``ResearchEvidenceSummaryResponse``
(+ export). Copy from ``latest_assessment.coverage_confidence`` when present; otherwise
null. Never invent a value.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest probability confidence,
labeled as coverage (not probability).

### 3. Out of scope

New coverage math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0146-phase-145-evidence-summary-scan-label-counts.md](0146-phase-145-evidence-summary-scan-label-counts.md)
- [0149-phase-148-nas-live-verify-phase-147.md](0149-phase-148-nas-live-verify-phase-147.md)
