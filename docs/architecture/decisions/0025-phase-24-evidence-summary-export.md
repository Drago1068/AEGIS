# ADR-0025: Phase 24 Research Evidence Summary JSON Export

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 22 added authenticated `GET /research/{symbol}/evidence-summary`. Operators need the
same research-only aggregate as a downloadable JSON file for offline audit without inventing
fields or expanding product capabilities.

## Decisions

### 1. Export route

Authenticated:

- `GET /research/{symbol}/evidence-summary/export` — identical payload to
  `GET /research/{symbol}/evidence-summary` (`ResearchEvidenceSummaryResponse`), with:
  - `Content-Type: application/json`
  - `Content-Disposition: attachment; filename="aegis-{SYMBOL}-evidence-summary.json"`

Empty / missing pieces remain **null** or **0**. HTTP **200** even when no assessment exists.
`state` remains `research_only`. Do not invent confidence or labels.

### 2. Composition only

Reuse the same summary composition as Phase 22. No new persistence, methods, or client-side
research math.

### 3. Frontend

Operator console may offer a download control that calls the export route with session
credentials and saves the JSON file locally.

## Consequences

- Operators can archive a point-in-time research evidence snapshot without copy-paste.
- Auth and fail-closed null/zero semantics stay aligned with the interactive summary.

## Explicitly out of scope

- Multi-horizon method changes
- Default-on automatic calibration
- Actionable promotion, recommendations, orders
- Portfolio-level dashboards
- CSV / PDF / non-JSON formats

## Related documents

- [0023-phase-22-research-evidence-summary.md](0023-phase-22-research-evidence-summary.md)
- [0024-phase-23-nas-live-verify-phase-22.md](0024-phase-23-nas-live-verify-phase-22.md)
- [../overview.md](../overview.md)
