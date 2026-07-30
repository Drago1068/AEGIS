# ADR-0044: Phase 43 Historical Outcome-Label Backfill

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 13–14 added on-demand and post-assessment `forward_total_return_v1` labeling.
Assessments that fail closed at create time (insufficient forward bars) are not retried when
bars later become available. Live NAS verification after Phase 41 shows thin corpora
(`insufficient_labeled_corpus`) with assessments present and zero labels. Operators need a
research-only way to re-attempt labeling over recent assessment history without enabling
automatic calibration or inventing confidence.

## Decisions

### 1. Scope

Add authenticated **batch backfill** of Phase 13 outcome labels for a symbol:

1. List up to ``limit`` assessments (newest first; same bound as assessment list: 1–100).
2. For each assessment with an id, call existing ``OutcomeLabelService.label_assessment`` via
   ``run_outcome_labels_after_assessments`` (Phase 14 fail-closed batch helper).
3. Return a summary: ``assessment_count``, ``persisted_count``, ``skipped_count``, and
   per-assessment outcomes (``persisted``, optional ``reason`` / ``detail``).
4. Always **HTTP 200** for the batch (partial skips are expected); single-assessment
   ``POST .../assessments/{id}/outcome-labels`` remains the strict **422** path.

### 2. API and console

- ``POST /research/{symbol}/outcome-labels/backfill?limit=`` (default 20).
- Operator console: "Backfill outcome labels" control with research-only copy.
- No change to ``AEGIS_RESEARCH_OUTCOME_LABEL_AFTER_ASSESSMENT_ENABLED`` or
  ``AEGIS_RESEARCH_CALIBRATION_AFTER_LABEL_ENABLED`` defaults.

### 3. Evidence rules

- Append-only labels only; never invent ``probability_confidence``.
- Re-labeling an already-labeled assessment may append another row (history-preserving);
  corpus readers continue to use the newest label per assessment.
- Skip reasons reuse Phase 13 ``OutcomeLabelReason`` values (plus ``unexpected_error``).

### 4. Out of scope

- Default-on / automatic calibration
- New horizons beyond 5/20
- Guaranteeing readiness becomes ``ready``
- Actionable promotion, recommendations, orders
- ACME / public TLS

## Related documents

- [0014-phase-13-research-outcome-labels.md](0014-phase-13-research-outcome-labels.md)
- [0015-phase-14-scheduled-outcome-labels.md](0015-phase-14-scheduled-outcome-labels.md)
- [0042-phase-41-multi-horizon-calibration.md](0042-phase-41-multi-horizon-calibration.md)
- [0043-phase-42-nas-live-verify-phase-41.md](0043-phase-42-nas-live-verify-phase-41.md)
