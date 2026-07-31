# ADR-0148: Phase 147 Evidence Summary Latest Coverage Confidence

- Status: Accepted
- Date: 2026-07-30

## Context

Evidence summary already surfaces latest ``probability_confidence`` (from calibration) and
keeps coverage confidence nested under ``latest_assessment``. Operators benefit from an
explicit top-level ``latest_coverage_confidence`` so coverage vs probability remain
visually and contractually separate (project rule). Panel UI modularization is complete;
prefer product/evidence work.

## Decisions

### 1. API

Add ``latest_coverage_confidence: float | null`` to ``ResearchEvidenceSummaryResponse``
(and export). Source from ``latest_assessment.coverage_confidence`` when present; null when
no assessment. Never invent a value.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest probability_confidence,
with a short note that coverage confidence is distinct from probability confidence.

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, further UI structural extracts.

## Related documents

- [0023-phase-22-research-evidence-summary.md](0023-phase-22-research-evidence-summary.md)
- [0149-phase-148-nas-live-verify-phase-147.md](0149-phase-148-nas-live-verify-phase-147.md)
