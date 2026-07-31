# ADR-0230: Phase 229 Evidence Summary Scan-Labeled Freshness Lag

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 213–228 completed the planned scan-labeled scalar provenance lift
(``most_recent_labeled_outcome_label_*``). Live NAS evidence repeatedly shows AAPL with
``latest_outcome_label_id=null`` while scan-labeled fields are non-null. Operators can now
see both ``latest_as_of_trading_date`` and ``most_recent_labeled_outcome_label_as_of_trading_date``
but still mentally subtract them to understand how stale the labeled corpus is relative to the
absolute latest assessment.

That gap is an **evidence diagnostic**, not another nested extract: a top-level lag integer
makes unlabeled/labeled freshness fail-closed and auditable without inventing probabilities.

## Decisions

### 1. API

Add ``scan_labeled_freshness_lag_trading_days: int | null`` to
``ResearchEvidenceSummaryResponse`` (+ export):

- When both ``latest_as_of_trading_date`` and
  ``most_recent_labeled_outcome_label_as_of_trading_date`` are present, set to the
  non-negative **exchange trading-day** count strictly after the labeled as_of through the
  latest as_of inclusive (same helper as assessment staleness:
  ``count_trading_days_strictly_between`` on ``AEGIS`` ``exchange_calendar_name``, default
  NYSE).
- Null when either date is missing. Clamp to 0 if inverted. Never invent dates.

### 2. Console

Surface near scan-labeled as_of
(``data-testid="evidence-scan-labeled-freshness-lag-trading-days"``).

### 3. Explicitly out of scope

- More nested UI modularization extracts
- Redundant scalar copies of already-lifted nested fields
- Default-on calibration, actionable promotion, orders, new scoring math

### 4. Why this next (not more scalars)

Scan-labeled identity/provenance scalars are complete. The remaining operator pain is
**interpreting the unlabeled gap**. Lag is derived evidence from existing dates, not a new
nested dig.

## Related documents

- [0228-phase-227-evidence-summary-most-recent-labeled-outcome-label-as-of-trading-date.md](0228-phase-227-evidence-summary-most-recent-labeled-outcome-label-as-of-trading-date.md)
- [0229-phase-228-nas-live-verify-phase-227.md](0229-phase-228-nas-live-verify-phase-227.md)
- [0231-phase-230-nas-live-verify-phase-229.md](0231-phase-230-nas-live-verify-phase-229.md)
