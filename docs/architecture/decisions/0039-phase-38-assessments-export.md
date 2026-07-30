# ADR-0039: Phase 38 Assessment History JSON Export

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 10 and 28 expose append-only research assessment history in the API and console.
Operators need that history as a downloadable JSON file for offline audit, matching the
outcome-labels, calibrations, and evidence-summary export pattern, without inventing
coverage/probability confidence or promoting research-only state.

## Decisions

### 1. Export route

Authenticated:

- `GET /research/{symbol}/assessments/export?limit=` — identical JSON array payload to
  `GET /research/{symbol}/assessments?limit=` (`limit` default 20, max 100), with:
  - `Content-Type: application/json`
  - `Content-Disposition: attachment; filename="aegis-{SYMBOL}-assessments.json"`

Empty history returns **200** with `[]`. Do not invent assessments or confidence values.
Preserve the same calibration enrichment as the interactive list route.

### 2. Composition only

Reuse `ResearchAssessmentService.list_assessments` and
`enrich_assessment_with_calibration`. No new persistence or methods.

### 3. Frontend

Operator console may offer a download control for assessment history.

## Consequences

- Operators can archive assessment history without copy-paste.
- Auth and fail-closed null/omit semantics stay aligned with the list route.

## Explicitly out of scope

- Default-on automatic calibration
- New assessment methods or horizons
- Actionable promotion, recommendations, orders
- TLS cutover
- CSV / PDF / non-JSON formats

## Related documents

- [0035-phase-34-outcome-labels-export.md](0035-phase-34-outcome-labels-export.md)
- [0037-phase-36-calibrations-export.md](0037-phase-36-calibrations-export.md)
- [0025-phase-24-evidence-summary-export.md](0025-phase-24-evidence-summary-export.md)
- [../overview.md](../overview.md)
