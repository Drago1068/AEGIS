# ADR-0170: Phase 169 Evidence Summary Latest Event Time

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes method, lookback, schema, and ``computed_at`` for the latest
assessment. Operators still dig into nested ``latest_assessment.event_time`` to confirm the
observation/event timestamp used for the snapshot. A top-level field keeps event timing
visible without inventing timestamps.

## Decisions

### 1. API

Add ``latest_event_time: datetime | null`` to ``ResearchEvidenceSummaryResponse`` (+ export).
Copy from ``latest_assessment.event_time`` when present; otherwise null. Never invent.
JSON serialization remains ISO-8601.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near computed_at
(``data-testid="evidence-latest-event-time"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0168-phase-167-evidence-summary-latest-computed-at.md](0168-phase-167-evidence-summary-latest-computed-at.md)
- [0171-phase-170-nas-live-verify-phase-169.md](0171-phase-170-nas-live-verify-phase-169.md)
