# ADR-0033: Phase 32 Calibration Readiness JSON Export

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 16 added authenticated `GET /research/{symbol}/calibration-readiness`. Operators need
the same research-only diagnostic as a downloadable JSON file for offline audit, matching
the evidence-summary export pattern (Phase 24) without inventing corpus or probability fields.

## Decisions

### 1. Export route

Authenticated:

- `GET /research/{symbol}/calibration-readiness/export` — identical payload to
  `GET /research/{symbol}/calibration-readiness` (`CalibrationReadinessResponse`), with:
  - `Content-Type: application/json`
  - `Content-Disposition: attachment; filename="aegis-{SYMBOL}-calibration-readiness.json"`

Diagnostics only; does not persist calibration rows or invent `probability_confidence`.

### 2. Composition only

Reuse existing readiness evaluation. No new persistence or methods.

### 3. Frontend

Operator console may offer a download control that calls the export route with session
credentials and saves the JSON file locally.

## Consequences

- Operators can archive readiness diagnostics without copy-paste.
- Auth and fail-closed semantics stay aligned with the interactive readiness endpoint.

## Explicitly out of scope

- Default-on automatic calibration
- Horizon-specific calibration methods
- Actionable promotion, recommendations, orders
- TLS cutover
- CSV / PDF / non-JSON formats

## Related documents

- [0017-phase-16-calibration-readiness.md](0017-phase-16-calibration-readiness.md)
- [0025-phase-24-evidence-summary-export.md](0025-phase-24-evidence-summary-export.md)
- [../overview.md](../overview.md)
