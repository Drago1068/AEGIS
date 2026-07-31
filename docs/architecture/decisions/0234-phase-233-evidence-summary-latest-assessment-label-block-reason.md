# ADR-0234: Phase 233 Evidence Summary Latest Assessment Label Block Reason

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 231–232 closed ``latest_assessment_is_label_ready``. Live AAPL evidence shows
``False`` with unlabeled latest and lag=119. Operators know the latest row *cannot* be
labeled today, but not *which fail-closed gate* blocked it.

## Decisions

### 1. API

Add ``latest_assessment_label_block_reason: str | null`` to
``ResearchEvidenceSummaryResponse`` (+ export):

- Null when no latest assessment, or when label-ready.
- When not ready, set to ``OutcomeLabelReason`` value from
  ``snapshot_label_block_reason`` / ``label_readiness_for_assessment``
  (``no_as_of_bar`` | ``insufficient_forward_bars``). Never invent.
- ``already_labeled`` is out of scope; operators use ``latest_outcome_label_id``.

### 2. Console

Surface near label-ready
(``data-testid="evidence-latest-assessment-label-block-reason"``).

### 3. Explicitly out of scope

Nested UI extracts, redundant scalar lifts, default-on calibration, orders, new scoring math.

## Related documents

- [0232-phase-231-evidence-summary-latest-assessment-is-label-ready.md](0232-phase-231-evidence-summary-latest-assessment-is-label-ready.md)
- [0233-phase-232-nas-live-verify-phase-231.md](0233-phase-232-nas-live-verify-phase-231.md)
- [0235-phase-234-nas-live-verify-phase-233.md](0235-phase-234-nas-live-verify-phase-233.md)
