# ADR-0037: Phase 36 Calibration History JSON Export

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 18–19 and 28 expose append-only probability calibration history in the API and
console. Operators need that history as a downloadable JSON file for offline audit,
matching the outcome-labels and calibration-readiness export pattern, without inventing
confidence values or promoting research-only state.

## Decisions

### 1. Export route

Authenticated:

- `GET /research/{symbol}/assessments/{assessment_id}/calibrations/export?limit=` —
  identical JSON array payload to
  `GET /research/{symbol}/assessments/{assessment_id}/calibrations?limit=`
  (`limit` default 20, max 100), with:
  - `Content-Type: application/json`
  - `Content-Disposition: attachment; filename="aegis-{SYMBOL}-assessment-{id}-calibrations.json"`

Empty history returns **200** with `[]`. Do not invent calibrations or confidence.

### 2. Composition only

Reuse `ResearchProbabilityCalibrationService.list_calibrations_for_assessment`. No new
persistence or methods.

### 3. Frontend

Operator console may offer a download control when the current assessment id is known.

## Consequences

- Operators can archive calibration history without copy-paste.
- Auth and fail-closed null/omit semantics stay aligned with the list route.

## Explicitly out of scope

- Default-on automatic calibration
- New calibration methods or horizons
- Actionable promotion, recommendations, orders
- TLS cutover
- CSV / PDF / non-JSON formats

## Related documents

- [0019-phase-18-on-demand-calibration.md](0019-phase-18-on-demand-calibration.md)
- [0035-phase-34-outcome-labels-export.md](0035-phase-34-outcome-labels-export.md)
- [0033-phase-32-calibration-readiness-export.md](0033-phase-32-calibration-readiness-export.md)
- [../overview.md](../overview.md)
