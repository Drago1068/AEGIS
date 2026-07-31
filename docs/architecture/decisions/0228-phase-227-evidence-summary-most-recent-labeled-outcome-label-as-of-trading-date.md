# ADR-0228: Phase 227 Evidence Summary Most Recent Labeled Outcome Label As-Of Trading Date

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes scan-labeled ``most_recent_labeled_outcome_label_computed_at``.
Operators still dig into ``most_recent_labeled_outcome_label.as_of_trading_date`` when the
absolute latest assessment is unlabeled. A top-level field keeps that trading date visible
without inventing values. Distinct from ``latest_outcome_label_as_of_trading_date`` and
assessment ``latest_as_of_trading_date``. This completes the planned scan-labeled scalar
provenance series.

## Decisions

### 1. API

Add ``most_recent_labeled_outcome_label_as_of_trading_date: date | null`` to
``ResearchEvidenceSummaryResponse`` (+ export). Copy from
``most_recent_labeled_outcome_label.as_of_trading_date`` when present; otherwise null. Never
invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near most recent labeled computed_at
(``data-testid="evidence-most-recent-labeled-outcome-label-as-of-trading-date"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts, additional
redundant nested field lifts.

## Related documents

- [0226-phase-225-evidence-summary-most-recent-labeled-outcome-label-computed-at.md](0226-phase-225-evidence-summary-most-recent-labeled-outcome-label-computed-at.md)
- [0229-phase-228-nas-live-verify-phase-227.md](0229-phase-228-nas-live-verify-phase-227.md)
- [0230-phase-229-evidence-summary-scan-labeled-freshness-lag.md](0230-phase-229-evidence-summary-scan-labeled-freshness-lag.md)
