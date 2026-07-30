# ADR-0058: Phase 57 Source-Aware Label Backfill Throughput

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 56 live evidence grew AAPL assessments to ~100 with deeper Polygon history and
cross-source fill. Outcome-label backfill with ``limit=100`` still selected candidates that
failed at compute (``insufficient_forward_bars`` / ``no_as_of_bar``) because Phase 49
readiness used **any-source** closes while Phase 13 labeling indexes closes by the
resolved assessment ``bar_source``. Those false-ready rows burned the operator limit.
Console and API defaults of ``limit=20`` also capped labeling throughput below the scan
window.

## Decisions

### 1. Source-aware label readiness

``select_backfill_candidates`` / ``is_snapshot_label_ready`` require the same resolved
label bar source as ``compute_forward_total_return_labels``:

- as-of close present for that source
- closes present for **every** ``FORWARD_HORIZON_SESSIONS`` end date (5 and 20)

False-ready rows that would fail closed at compute are omitted before the batch (not
reported as skips). Fail-closed compute gates are unchanged.

### 2. Throughput defaults

- ``BACKFILL_SCAN_LIMIT`` raised from **100** to **252** (aligned with default research
  bar load).
- API ``POST .../outcome-labels/backfill`` default ``limit`` raised from **20** to
  **100**; upper bound **252**.
- Research console backfill uses ``limit=100``.

Verify scripts may retain ``limit=20`` for Phase 48/50 coupling checks.

### 3. Out of scope

- Weakening forward-bar or no-as-of gates
- Default-on calibration
- Auto-chaining assessment → label backfill
- Actionable promotion, orders, ACME
- NAS live verify (follow-up ops phase)

## Related documents

- [0050-phase-49-prefer-unlabeled-label-backfill.md](0050-phase-49-prefer-unlabeled-label-backfill.md)
- [0057-phase-56-nas-live-verify-phase-55.md](0057-phase-56-nas-live-verify-phase-55.md)
- [0014-phase-13-research-outcome-labels.md](0014-phase-13-research-outcome-labels.md)
- [../../operations/configuration.md](../../operations/configuration.md)
