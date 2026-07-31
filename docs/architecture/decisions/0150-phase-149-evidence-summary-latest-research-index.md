# ADR-0150: Phase 149 Evidence Summary Latest Research Index

- Status: Proposed
- Date: 2026-07-30

## Context

Evidence summary now exposes top-level ``latest_coverage_confidence`` and nested
probability confidence. Operators still dig into ``latest_assessment.components`` (or the
detail section) for the research index that drives calibration bucketing. A top-level
``latest_research_index`` keeps the summary self-sufficient without inventing values.

## Decisions

### 1. API

Add ``latest_research_index: float | null`` to ``ResearchEvidenceSummaryResponse`` (+ export).
Source from the latest assessment ``components.research_index`` when present; otherwise
null. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near coverage/probability rows.

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0148-phase-147-evidence-summary-latest-coverage-confidence.md](0148-phase-147-evidence-summary-latest-coverage-confidence.md)
- [0151-phase-150-nas-live-verify-phase-149.md](0151-phase-150-nas-live-verify-phase-149.md)
