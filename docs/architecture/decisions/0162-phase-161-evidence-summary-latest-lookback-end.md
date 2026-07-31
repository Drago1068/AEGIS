# ADR-0162: Phase 161 Evidence Summary Latest Lookback End Date

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes method id/version, as-of date, bar count, and input source
for the latest assessment. Operators still dig into nested
``latest_assessment.lookback_end_date`` to see the end of the bar window that fed the
snapshot. A top-level field keeps the lookback window visible without inventing dates.

## Decisions

### 1. API

Add ``latest_lookback_end_date: date | null`` to ``ResearchEvidenceSummaryResponse``
(+ export). Copy from ``latest_assessment.lookback_end_date`` when present; otherwise
null. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near as-of / bar count
(``data-testid="evidence-latest-lookback-end-date"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts,
``lookback_start_date`` (defer if needed).

## Related documents

- [0160-phase-159-evidence-summary-latest-method-version.md](0160-phase-159-evidence-summary-latest-method-version.md)
- [0163-phase-162-nas-live-verify-phase-161.md](0163-phase-162-nas-live-verify-phase-161.md)
