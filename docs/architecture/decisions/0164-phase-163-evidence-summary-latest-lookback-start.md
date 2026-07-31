# ADR-0164: Phase 163 Evidence Summary Latest Lookback Start Date

- Status: Proposed
- Date: 2026-07-31

## Context

Evidence summary now exposes ``latest_lookback_end_date`` for the latest assessment.
Operators still dig into nested ``latest_assessment.lookback_start_date`` to see the start
of the bar window. Pairing start with end completes lookback-window provenance without
inventing dates.

## Decisions

### 1. API

Add ``latest_lookback_start_date: date | null`` to ``ResearchEvidenceSummaryResponse``
(+ export). Copy from ``latest_assessment.lookback_start_date`` when present; otherwise
null. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near lookback end / as-of
(``data-testid="evidence-latest-lookback-start-date"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0162-phase-161-evidence-summary-latest-lookback-end.md](0162-phase-161-evidence-summary-latest-lookback-end.md)
- [0165-phase-164-nas-live-verify-phase-163.md](0165-phase-164-nas-live-verify-phase-163.md)
