# ADR-0232: Phase 231 Evidence Summary Latest Assessment Is Label Ready

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 229–230 closed the scan-labeled freshness lag diagnostic. Live NAS evidence for AAPL
shows ``latest_outcome_label_id=null``, ``scan_labeled_freshness_lag_trading_days=119``, and
a non-null scan-labeled row. Operators can see *how stale* labels are, but not *whether the
absolute latest assessment can be labeled today*.

Existing domain helper ``is_snapshot_label_ready`` already encodes forward-bar gates. Surfacing
a top-level boolean is an **evidence diagnostic**, not another nested provenance scalar lift.

## Decisions

### 1. API

Add ``latest_assessment_is_label_ready: bool | null`` to ``ResearchEvidenceSummaryResponse``
(+ export):

- When a latest assessment exists, evaluate via
  ``OutcomeLabelService.is_assessment_label_ready`` (loads stored bars; reuses
  ``is_snapshot_label_ready`` with exchange calendar / horizons). Never invent closes.
- Null when no latest assessment.

### 2. Console

Surface near freshness lag
(``data-testid="evidence-latest-assessment-is-label-ready"``).

### 3. Explicitly out of scope

- Nested UI modularization extracts
- Redundant copies of already-lifted scalar provenance fields
- ``latest_assessment_label_block_reason`` (follow-on phase)
- Default-on calibration, actionable promotion, orders, new scoring math

## Related documents

- [0230-phase-229-evidence-summary-scan-labeled-freshness-lag.md](0230-phase-229-evidence-summary-scan-labeled-freshness-lag.md)
- [0231-phase-230-nas-live-verify-phase-229.md](0231-phase-230-nas-live-verify-phase-229.md)
- [0233-phase-232-nas-live-verify-phase-231.md](0233-phase-232-nas-live-verify-phase-231.md)
