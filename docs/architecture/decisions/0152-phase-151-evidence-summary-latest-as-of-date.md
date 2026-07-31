# ADR-0152: Phase 151 Evidence Summary Latest As-Of Trading Date

- Status: Accepted
- Date: 2026-07-30

## Context

Evidence summary now surfaces top-level coverage confidence and research index for the
latest assessment. Operators still open nested ``latest_assessment`` to see the point-in-time
``as_of_trading_date`` that anchors the snapshot. A top-level field makes the summary
self-describing without inventing dates.

## Decisions

### 1. API

Add ``latest_as_of_trading_date: date | null`` to ``ResearchEvidenceSummaryResponse``
(+ export). Copy from ``latest_assessment.as_of_trading_date`` when present; otherwise null.
Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near research index / coverage rows
(``data-testid="evidence-latest-as-of-trading-date"``; ISO date or ``null``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0150-phase-149-evidence-summary-latest-research-index.md](0150-phase-149-evidence-summary-latest-research-index.md)
- [0153-phase-152-nas-live-verify-phase-151.md](0153-phase-152-nas-live-verify-phase-151.md)
