# ADR-0154: Phase 153 Evidence Summary Latest Bar Count

- Status: Proposed
- Date: 2026-07-30

## Context

Evidence summary now exposes top-level research index, coverage confidence, and as-of
trading date for the latest assessment. Operators still dig into nested
``latest_assessment.bar_count`` to see how many usable bars fed the snapshot. A top-level
field keeps coverage context visible without inventing counts.

## Decisions

### 1. API

Add ``latest_bar_count: int | null`` to ``ResearchEvidenceSummaryResponse`` (+ export).
Copy from ``latest_assessment.bar_count`` when present; otherwise null. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near as-of / research index rows.

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0152-phase-151-evidence-summary-latest-as-of-date.md](0152-phase-151-evidence-summary-latest-as-of-date.md)
- [0155-phase-154-nas-live-verify-phase-153.md](0155-phase-154-nas-live-verify-phase-153.md)
