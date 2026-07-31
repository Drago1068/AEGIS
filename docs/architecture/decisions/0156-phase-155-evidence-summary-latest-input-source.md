# ADR-0156: Phase 155 Evidence Summary Latest Input Source

- Status: Accepted
- Date: 2026-07-30

## Context

Evidence summary now exposes top-level research index, coverage confidence, as-of date, and
bar count for the latest assessment. Operators still dig into nested
``latest_assessment.input_source`` (distinct from ``latest_component_source``) to see the
primary observation source that fed the snapshot. A top-level field keeps provenance visible
without inventing sources.

## Decisions

### 1. API

Add ``latest_input_source: str | null`` to ``ResearchEvidenceSummaryResponse`` (+ export).
Copy from ``latest_assessment.input_source`` when present; otherwise null. Never invent.
Keep distinct from ``latest_component_source`` (which may be ``mixed``).

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near component source / bar count
(``data-testid="evidence-latest-input-source"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0154-phase-153-evidence-summary-latest-bar-count.md](0154-phase-153-evidence-summary-latest-bar-count.md)
- [0157-phase-156-nas-live-verify-phase-155.md](0157-phase-156-nas-live-verify-phase-155.md)
