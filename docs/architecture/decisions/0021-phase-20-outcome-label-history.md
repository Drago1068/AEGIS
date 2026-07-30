# ADR-0021: Phase 20 Outcome Label History

- Status: Accepted
- Date: 2026-07-29

## Context

Phase 13/14 added append-only `forward_total_return_v1` outcome labels with on-demand and
scheduled create paths, plus `GET .../outcome-labels/latest`. Phase 19 added calibration
history. Operators still could not inspect the append-only trail of repeated label computes
for an assessment.

## Decisions

### 1. List route

Authenticated:

- `GET /research/{symbol}/assessments/{assessment_id}/outcome-labels?limit=` — up to `limit`
  (default 20, max 100) label rows for that assessment, **newest `computed_at` first**.
  Rows are restricted to the path `symbol` (case-insensitive). Empty list when none match;
  do **not** invent label values.

Existing `GET .../outcome-labels/latest` and `POST .../outcome-labels` remain unchanged.

### 2. Persistence and method

- Reuse append-only `research_assessment_outcome_labels`; no new tables or label methods.
- No in-place updates to assessment snapshots.

### 3. Frontend

Operator console may load and display outcome-label history for the current assessment
(compact list when more than one row). Values stay evidence-only; no client-side labeling.

### 4. State separation

Label rows keep `state = research_only`. No probability calibration inventing. Coverage and
probability confidence remain separate.

## Consequences

- Operators can audit repeated labeling the same way as calibration history (ADR-0020).
- Empty history is a normal 200 with `[]`.

## Explicitly out of scope

- Multi-horizon method changes
- Default-on automatic calibration
- Actionable promotion, recommendations, orders

## Related documents

- [0014-phase-13-research-outcome-labels.md](0014-phase-13-research-outcome-labels.md)
- [0020-phase-19-calibration-history.md](0020-phase-19-calibration-history.md)
- [../overview.md](../overview.md)
