# ADR-0158: Phase 157 Evidence Summary Latest Method Id

- Status: Proposed
- Date: 2026-07-30

## Context

Evidence summary now exposes top-level research index, coverage confidence, as-of date,
bar count, and input source for the latest assessment. Operators still dig into nested
``latest_assessment.method_id`` to see which research method produced the snapshot. A
top-level field keeps method provenance visible without inventing identifiers.

## Decisions

### 1. API

Add ``latest_method_id: str | null`` to ``ResearchEvidenceSummaryResponse`` (+ export).
Copy from ``latest_assessment.method_id`` when present; otherwise null. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near input source / bar count
(``data-testid="evidence-latest-method-id"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts,
``method_version`` (defer to a later phase if needed).

## Related documents

- [0156-phase-155-evidence-summary-latest-input-source.md](0156-phase-155-evidence-summary-latest-input-source.md)
- [0159-phase-158-nas-live-verify-phase-157.md](0159-phase-158-nas-live-verify-phase-157.md)
