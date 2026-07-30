# ADR-0050: Phase 49 Prefer Unlabeled Label-Ready Outcome-Label Backfill

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 43 outcome-label backfill listed the newest ``limit`` assessments and attempted each.
Already-labeled rows burned the limit (appending duplicate history), and tip assessments without
forward bars failed ``insufficient_forward_bars`` before older label-ready rows were reached.
Phase 48 verify worked around this with ``limit=100``. Operators need the default ``limit=20``
path to prefer work that can grow the labeled corpus.

## Decisions

### 1. Candidate selection

``POST .../outcome-labels/backfill``:

1. Scans up to ``BACKFILL_SCAN_LIMIT`` (100) recent assessments (newest first).
2. Omits assessments that already have a stored label for ``forward_total_return_v1``
   (``LABEL_METHOD_ID``).
3. Omits assessments whose ``as_of`` lacks a stored close on the max forward-horizon end
   session (same gate as Phase 47 / ``has_stored_forward_horizon_close``), using the label
   service bar load.
4. Takes the first ``limit`` remaining candidates and runs Phase 14
   ``run_outcome_labels_after_assessments``.

Omitted rows are not reported as skip outcomes (they never enter the batch).

### 2. Scope

- Domain selection helper + store batch lookup of labeled assessment ids + router wiring.
- Verify scripts may use ``limit=20`` again for outcome-label backfill; Phase 48 coupling
  remains when assessments ``persisted_count > 0``.
- Console copy unchanged aside from docs.

### 3. Out of scope

- Raising ``BAR_LOAD_LIMIT``
- Auto-chaining assessment → label backfill
- Default-on calibration
- Guaranteeing readiness ``ready``
- Actionable promotion, orders, ACME

## Supersession note

Phase 57 / ADR-0058 keeps this selection order but makes readiness **source-aware**
(matching Phase 13 compute), raises ``BACKFILL_SCAN_LIMIT`` to 252, and raises API/console
default ``limit`` to 100.

## Related documents

- [0044-phase-43-outcome-label-backfill.md](0044-phase-43-outcome-label-backfill.md)
- [0048-phase-47-label-ready-assessment-backfill.md](0048-phase-47-label-ready-assessment-backfill.md)
- [0049-phase-48-nas-live-verify-phase-47.md](0049-phase-48-nas-live-verify-phase-47.md)
- [0014-phase-13-research-outcome-labels.md](0014-phase-13-research-outcome-labels.md)
