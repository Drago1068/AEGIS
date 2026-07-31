# ADR-0240: Phase 239 Evidence Summary Scan Unlabeled Label-Ready Count

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 237–238 added ``most_recent_unlabeled_labelable_as_of_trading_date``. Live AAPL showed
that field **null** while ``unlabeled_assessment_count=3`` and
``most_recent_labelable_as_of_trading_date=2026-02-05`` (already labeled). Operators inferred
“no backfill work” from a null date; an explicit **count of unlabeled and label-ready** rows
in the scan makes emptiness fail-closed and auditable.

## Decisions

### 1. API

Add ``scan_unlabeled_label_ready_count: int`` (+ export):

- Count assessments in the newest-first scan that are unlabeled **and**
  ``is_snapshot_label_ready``.
- Always a non-negative integer; ``0`` when none (including empty scan). Never invent.
- Extend ``OutcomeLabelService.scan_label_diagnostics`` (one bar load).

### 2. Console

``data-testid="evidence-scan-unlabeled-label-ready-count"``.

### 3. Out of scope

UI modularization, redundant nested lifts, default-on calibration, orders.

## Consequences

- Evidence summary and export expose backfill-candidate cardinality.
- Phase 240 live-verifies the field on NAS (checklist item 115).

## Related documents

- [0238-phase-237-evidence-summary-most-recent-unlabeled-labelable-as-of.md](0238-phase-237-evidence-summary-most-recent-unlabeled-labelable-as-of.md)
- [0239-phase-238-nas-live-verify-phase-237.md](0239-phase-238-nas-live-verify-phase-237.md)
- [0241-phase-240-nas-live-verify-phase-239.md](0241-phase-240-nas-live-verify-phase-239.md)
