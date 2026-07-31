# ADR-0242: Phase 241 Evidence Summary Most Recent Unlabeled Assessment Id

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 237–240 established unlabeled+labelable as_of and
``scan_unlabeled_label_ready_count``. Live AAPL showed ``count=0`` with
``unlabeled_assessment_count=3`` and latest blocked
(``insufficient_forward_bars``). Operators inspecting the unlabeled tip need the
**assessment snapshot id** of the newest unlabeled row (for load / drill-down) without
scanning history by hand.

## Decisions

### 1. API

Add ``most_recent_unlabeled_assessment_id: int | null`` (+ export):

- Newest-first scan; first assessment with ``id`` not in labeled set wins.
- Null when none unlabeled. Never invent.
- Distinct from ``most_recent_labeled_assessment_id`` and ``latest_assessment_id``
  (equal to latest only when latest is unlabeled).

### 2. Console

``data-testid="evidence-most-recent-unlabeled-assessment-id"``.

### 3. Out of scope

UI modularization, inventing label-ready targets, default-on calibration, orders.

## Consequences

- Evidence summary and export expose the unlabeled tip id for drill-down.
- Phase 242 live-verifies the field on NAS (checklist item 116).

## Related documents

- [0240-phase-239-evidence-summary-scan-unlabeled-label-ready-count.md](0240-phase-239-evidence-summary-scan-unlabeled-label-ready-count.md)
- [0241-phase-240-nas-live-verify-phase-239.md](0241-phase-240-nas-live-verify-phase-239.md)
- [0243-phase-242-nas-live-verify-phase-241.md](0243-phase-242-nas-live-verify-phase-241.md)
