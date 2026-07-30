# ADR-0042: Phase 41 Multi-Horizon Probability Calibration

- Status: Accepted
- Date: 2026-07-30

## Context

Outcome labels already persist `forward_return_5` and `forward_return_20`. Probability
calibration hard-coded `forward_return_5`, so 20-session labels never informed calibrated
confidence. Operators need horizon-specific research-only calibrations without inventing
values or promoting state.

## Decisions

### 1. Persist horizon on calibration rows

Alembic `0009` adds non-null `outcome_horizon_key` (backfill existing rows to
`forward_return_5`). Method id remains `research_calibration_v1`; method version bumps to
`2`.

### 2. Supported horizons

`OUTCOME_HORIZON_KEYS = ("forward_return_5", "forward_return_20")`. Corpus examples and
positive-rate use the selected horizon’s label value. Missing horizons are fail-closed (no
invented returns).

### 3. API

`POST .../calibrations?horizon=` defaults to `forward_return_5` and returns one row.
Unsupported horizons return **422**. List/export include `outcome_horizon_key`.

### 4. Readiness

`GET .../calibration-readiness` evaluates each supported horizon into `by_horizon[]`.
Top-level `status` / counts remain the primary (`forward_return_5`) gate for backward
compatibility. Never invents `probability_confidence`.

### 5. Console

Surfaces horizon on readiness and calibration history. “Compute calibration” POSTs each
horizon marked `ready` in `by_horizon` (sequential).

## Explicitly out of scope

- New label horizons beyond 5/20
- Default-on automatic calibration
- Actionable promotion, recommendations, orders
- TLS changes
- CSV / PDF

## Related documents

- [0016-phase-15-research-probability-calibration.md](0016-phase-15-research-probability-calibration.md)
- [0027-phase-26-multi-horizon-label-surfacing.md](0027-phase-26-multi-horizon-label-surfacing.md)
- [0041-phase-40-nas-lab-tls-cutover.md](0041-phase-40-nas-lab-tls-cutover.md)
- [../overview.md](../overview.md)
