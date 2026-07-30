# ADR-0031: Phase 30 Outcome Label End-Date Surfacing

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 13 outcome labels persist `label_end_dates` (trading date of each horizon end close)
alongside `labels`. Phases 26–28 surface horizon returns in the console and evidence summary,
but end dates remain hidden. Operators need those dates for audit without inventing values.

## Decisions

### 1. Display-only

No API, method, or persistence changes. When a `labels` key is shown, also show the matching
`label_end_dates[key]` **if present**. Missing end dates are omitted (not invented as empty
strings or fabricated calendars).

### 2. Surfaces

- Latest outcome-label detail block
- Outcome-label history compact lines
- Evidence-summary latest outcome-label rows

### 3. Ordering

Reuse Phase 26 key ordering for `forward_return_{N}`.

## Consequences

- Operators see return and horizon end trading date together when both exist on the payload.
- Fail-closed: no client-side calendar math.

## Explicitly out of scope

- New horizons or label methods
- Horizon-specific calibration
- Default-on automatic calibration
- Actionable promotion, recommendations, orders
- TLS cutover

## Related documents

- [0014-phase-13-research-outcome-labels.md](0014-phase-13-research-outcome-labels.md)
- [0027-phase-26-multi-horizon-label-surfacing.md](0027-phase-26-multi-horizon-label-surfacing.md)
- [../overview.md](../overview.md)
