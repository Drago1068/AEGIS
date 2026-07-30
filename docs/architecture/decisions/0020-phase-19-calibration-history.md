# ADR-0020: Phase 19 Calibration History

- Status: Accepted
- Date: 2026-07-29

## Context

Phase 18 added on-demand `POST` / `GET .../calibrations/latest` for a single newest
`research_calibration_v1` row. Operators still could not inspect the append-only trail of
calibrations for an assessment after repeated compute attempts or corpus changes.

## Decisions

### 1. List route

Authenticated:

- `GET /research/{symbol}/assessments/{assessment_id}/calibrations?limit=` — up to `limit`
  (default 20, max 100) calibration rows for that assessment, **newest `computed_at` first**.
  Rows are restricted to the path `symbol` (case-insensitive). Empty list when none match;
  do **not** invent confidence values.

Existing `GET .../calibrations/latest` and `POST .../calibrations` remain unchanged.

### 2. Persistence and method

- Reuse append-only `research_assessment_probability_calibrations`; no new tables or methods.
- No in-place updates to assessment snapshots; API overlays for latest remain Phase 15/18.

### 3. Frontend

Operator console may load and display calibration history for the current assessment (compact
table or list). Values stay labeled research-only; no client-side calibration math.

### 4. State separation

Calibration rows keep `state = research_only`. Coverage and probability confidence stay
separate. Automatic calibration flag remains default `false`.

## Consequences

- Operators can audit repeated calibrations without enabling actionable promotion.
- Empty history is a normal 200 with `[]`, not an invented probability.

## Explicitly out of scope

- Multi-horizon calibration methods
- Symbol-wide corpus dashboards beyond readiness
- Default-on automatic calibration
- Actionable promotion, recommendations, orders

## Related documents

- [0016-phase-15-research-probability-calibration.md](0016-phase-15-research-probability-calibration.md)
- [0019-phase-18-on-demand-calibration.md](0019-phase-18-on-demand-calibration.md)
- [../overview.md](../overview.md)
