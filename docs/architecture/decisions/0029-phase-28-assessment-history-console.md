# ADR-0029: Phase 28 Research Assessment History in the Console

- Status: Accepted
- Date: 2026-07-30

## Context

Authenticated `GET /research/{symbol}/assessments?limit=` and the frontend
`listResearchAssessments` client already exist. The operator console still shows only the
latest assessment, while outcome-label and calibration histories are visible. Operators need
append-only assessment history for audit without inventing metrics.

## Decisions

### 1. Display-only list

When the operator refreshes latest or runs an assessment, the console also loads up to 20
newest assessments via the existing list route and renders a compact history when more than
one row is returned.

Each row shows API fields only:

- `computed_at`
- `components.research_index` (as present on the payload)
- `coverage_confidence`
- `probability_confidence` (display `null` when null — never merge with coverage)

No client-side research math, scoring, or recommendations.

### 2. Empty / single

Empty list clears history. A single assessment does not show a separate history block
(same pattern as label/calibration history).

### 3. No API changes

Reuse `GET /research/{symbol}/assessments?limit=`. No new tables, methods, or enrichment.

## Consequences

- Assessment append history is visible alongside label and calibration histories.
- Fail-closed null probability remains explicit in the UI.

## Explicitly out of scope

- New assessment methods or horizons
- Horizon-specific calibration
- Default-on automatic calibration
- Actionable promotion, recommendations, orders
- TLS cutover

## Related documents

- [0007-phase-6-research-only-scoring.md](0007-phase-6-research-only-scoring.md)
- [0027-phase-26-multi-horizon-label-surfacing.md](0027-phase-26-multi-horizon-label-surfacing.md)
- [../overview.md](../overview.md)
