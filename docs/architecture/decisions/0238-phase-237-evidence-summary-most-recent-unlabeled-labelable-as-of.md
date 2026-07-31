# ADR-0238: Phase 237 Evidence Summary Most Recent Unlabeled Labelable As-Of

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 235–236 added ``most_recent_labelable_as_of_trading_date`` (any label-ready row,
labeled or not). Live AAPL showed that date equal to
``most_recent_labeled_outcome_label_as_of_trading_date`` (``2026-02-05``) while latest remains
blocked (``insufficient_forward_bars``). Operators targeting **outcome-label backfill** need
the newest as_of that is **both unlabeled and label-ready** — otherwise the labelable date
points at work already done.

## Decisions

### 1. API

Add ``most_recent_unlabeled_labelable_as_of_trading_date: date | null`` (+ export):

- Walk assessments newest-first; first with ``is_snapshot_label_ready`` and no existing
  outcome label for the method wins.
- Null when none. Never invent.
- Extend ``OutcomeLabelService.scan_label_diagnostics`` (one bar load) to return the field.

### 2. Console

``data-testid="evidence-most-recent-unlabeled-labelable-as-of-trading-date"``.

### 3. Out of scope

UI modularization, redundant nested lifts, default-on calibration, orders.

### 4. Why this next

Labelable answered "what could be labeled." Unlabeled+labelable answers "what should backfill
do next?" — the remaining operator gap from live AAPL evidence.

## Consequences

- Evidence summary and export expose the backfill next-target as_of.
- Phase 238 live-verifies the field on NAS (checklist item 114).

## Related documents

- [0236-phase-235-evidence-summary-most-recent-labelable-as-of-trading-date.md](0236-phase-235-evidence-summary-most-recent-labelable-as-of-trading-date.md)
- [0237-phase-236-nas-live-verify-phase-235.md](0237-phase-236-nas-live-verify-phase-235.md)
- [0239-phase-238-nas-live-verify-phase-237.md](0239-phase-238-nas-live-verify-phase-237.md)
