# ADR-0027: Phase 26 Multi-Horizon Outcome Label Surfacing

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 13 outcome labels already compute `FORWARD_HORIZON_SESSIONS = (5, 20)` and persist
keys such as `forward_return_5` and `forward_return_20`. The operator console and evidence
summary still emphasize the 5-session horizon in compact history and summary rows, which
hides available research evidence.

## Decisions

### 1. Display-only surfacing

No API, method, horizon, or persistence changes. The console must render **every key present**
in each outcome-label `labels` object (and, when present, in
`evidence-summary.latest_outcome_label.labels`).

Missing keys are omitted (not invented as zero). Null latest label remains null.

### 2. Stable ordering

Horizon keys matching `forward_return_{N}` sort by ascending `N`. Other keys follow
localeCompare.

### 3. Compact history line

Outcome-label history rows format all present horizons (e.g. `fwd5=… · fwd20=…`) from the
API payload only — no client-side return math.

## Consequences

- Operators see the full configured label set already stored by Phase 13.
- Export JSON (Phase 24) already includes all keys; UI now matches.

## Explicitly out of scope

- New horizons or label methods
- Horizon-specific probability calibration
- Default-on automatic calibration
- Actionable promotion, recommendations, orders
- TLS cutover

## Related documents

- [0014-phase-13-research-outcome-labels.md](0014-phase-13-research-outcome-labels.md)
- [0023-phase-22-research-evidence-summary.md](0023-phase-22-research-evidence-summary.md)
- [../overview.md](../overview.md)
