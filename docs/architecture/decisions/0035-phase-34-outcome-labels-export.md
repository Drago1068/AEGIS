# ADR-0035: Phase 34 Outcome-Label History JSON Export

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 20 and 26–30 expose append-only outcome-label history in the API and console.
Operators need that history as a downloadable JSON file for offline audit, matching the
evidence-summary and calibration-readiness export pattern, without inventing returns or
end dates.

## Decisions

### 1. Export route

Authenticated:

- `GET /research/{symbol}/assessments/{assessment_id}/outcome-labels/export?limit=` —
  identical JSON array payload to
  `GET /research/{symbol}/assessments/{assessment_id}/outcome-labels?limit=`
  (`limit` default 20, max 100), with:
  - `Content-Type: application/json`
  - `Content-Disposition: attachment; filename="aegis-{SYMBOL}-assessment-{id}-outcome-labels.json"`

Empty history returns **200** with `[]`. Do not invent labels or end dates.

### 2. Composition only

Reuse `OutcomeLabelService.list_labels_for_assessment`. No new persistence or methods.

### 3. Frontend

Operator console may offer a download control when the current assessment id is known.

## Consequences

- Operators can archive label history without copy-paste.
- Auth and fail-closed null/omit semantics stay aligned with the list route.

## Explicitly out of scope

- New label methods or horizons
- Default-on automatic calibration
- Actionable promotion, recommendations, orders
- TLS cutover
- CSV / PDF / non-JSON formats

## Related documents

- [0021-phase-20-outcome-label-history.md](0021-phase-20-outcome-label-history.md)
- [0025-phase-24-evidence-summary-export.md](0025-phase-24-evidence-summary-export.md)
- [0033-phase-32-calibration-readiness-export.md](0033-phase-32-calibration-readiness-export.md)
- [../overview.md](../overview.md)
