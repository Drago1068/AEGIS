# ADR-0242: Phase 241 Evidence Summary Most Recent Unlabeled Assessment Id (draft)

- Status: Proposed (ready after Phase 240; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 237–240 established unlabeled+labelable as_of and
``scan_unlabeled_label_ready_count``. Live AAPL shows ``count=0`` with
``unlabeled_assessment_count=3`` and latest blocked
(``insufficient_forward_bars``). Operators inspecting the unlabeled tip need the
**assessment snapshot id** of the newest unlabeled row (for load / drill-down) without
scanning history by hand. The ready as_of is null; the unlabeled tip id is still known.

## Decisions (proposed)

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

### 4. Why this next

Count/date answered “how many / which as_of ready?” The id answers “which unlabeled row
to open first?” — the remaining operator gap when ready count is zero but unlabeled > 0.

## Resume (after Phase 240 gate)

```powershell
# Implement most_recent_unlabeled_assessment_id (ADR-0242); tests; commit+push; then Phase 242:
# git archive HEAD → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0240-phase-239-evidence-summary-scan-unlabeled-label-ready-count.md](0240-phase-239-evidence-summary-scan-unlabeled-label-ready-count.md)
- [0241-phase-240-nas-live-verify-phase-239.md](0241-phase-240-nas-live-verify-phase-239.md)
- [0243-phase-242-nas-live-verify-phase-241.md](0243-phase-242-nas-live-verify-phase-241.md)
