# ADR-0212: Phase 211 Evidence Summary Latest Outcome Label As-Of Trading Date

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary already exposes assessment ``latest_as_of_trading_date``. Operators still
want the persisted ``latest_outcome_label.as_of_trading_date`` as a top-level field that is
null whenever the latest assessment has no label row — never copying the assessment date into
that slot.

## Decisions

### 1. API

Add ``latest_outcome_label_as_of_trading_date: date | null`` to
``ResearchEvidenceSummaryResponse`` (+ export). Copy from
``latest_outcome_label.as_of_trading_date`` when present; otherwise null. Distinct from
assessment ``latest_as_of_trading_date``. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest outcome label bar_source
(``data-testid="evidence-latest-outcome-label-as-of-trading-date"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0210-phase-209-evidence-summary-latest-outcome-label-bar-source.md](0210-phase-209-evidence-summary-latest-outcome-label-bar-source.md)
- [0213-phase-212-nas-live-verify-phase-211.md](0213-phase-212-nas-live-verify-phase-211.md)
