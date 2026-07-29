# ADR-0007: Phase 6 Research-Only Scoring Foundations

- Status: Accepted
- Date: 2026-07-28

## Context

Phases 0 through 5 delivered foundation, daily-bar ingestion, scheduled watchlist ingest,
operator console, session authentication, and daily-bar charts. The data-model conventions
already require separate coverage and probability confidence fields and an explicit
research-only versus actionable state, but no domain module yet computed or stored either.

Phase 6 introduces the first research assessment over validated stored daily bars:
transparent, reproducible, fail-closed, and labeled research-only. It must not imply
actionable advice, calibrated probabilities, or order capability.

## Decisions

### 1. Scope

Backend domain, append-only persistence, authenticated HTTP API, and a read-only labeled
console panel on `/symbols/[symbol]`. No recommendations, no promotion to actionable, no
order UI, and no scheduler hook for assessments.

### 2. Method `daily_bar_research_v1`

One deterministic method id with `method_version = 1`:

- Input: the last 20 usable primary session bars for a symbol (chronological), from stored
  daily observations.
- `total_return_20 = close_n / close_0 - 1` (n = 19th index after the oldest close).
- `realized_vol_20` = sample standard deviation of the 19 daily log returns
  `ln(close_i / close_{i-1})`, annualized by `sqrt(252)`.
- `research_index = tanh(total_return_20 / max(realized_vol_20, epsilon))` with
  `epsilon = 1e-12`. This is a research heuristic in `[-1, 1]`, not a probability and not a
  trade signal.

### 3. Coverage confidence (exact formula)

```
bar_count_factor   = min(1, usable_primary_bars / 20)
primary_fraction  = usable_primary_bars / total_bars_in_lookback_window
freshness_factor  = 1 - (lag_trading_days / (max_staleness_trading_days + 1))
                    when lag_trading_days > 0;
                    else 1 when the latest bar's trading_date is on or after the most recent
                    exchange session on or before as_of
coverage_confidence = clip_to_[0,1](
  bar_count_factor * freshness_factor * primary_fraction
)
```

`lag_trading_days` counts exchange sessions strictly after the latest bar date up to and
including the expected latest session (same calendar helper pattern as ingest staleness).
`probability_confidence` is always `null` in Phase 6 (not calibrated). The two confidences
are never merged.

### 4. State and fail-closed

Every persisted and API-returned record has `state = "research_only"`. There is no write path
to `actionable` in this phase.

Fail closed (HTTP 422, structured `detail.reason`, persist nothing) when:

- fewer than 20 usable primary bars;
- any selected bar fails OHLCV usability (non-positive prices, inconsistent OHLC, negative
  volume);
- the latest bar is stale beyond `AEGIS_MAX_LATEST_BAR_STALENESS_TRADING_DAYS` versus the
  exchange calendar (same semantics as ingest latest-bar staleness).

Reason codes: `insufficient_primary_bars`, `unusable_ohlcv`, `stale_latest_bar`.

### 5. Storage and routes

Append-only plain Postgres table `research_assessment_snapshots` (not a Timescale hypertable).
Identity primary key; insert-only; always append on successful compute.

Authenticated routes (Phase 4 session gate):

- `POST /research/{symbol}/assessments` - compute and append
- `GET /research/{symbol}/assessments` - list newest-first
- `GET /research/{symbol}/assessments/latest` - latest or 404

On-demand only; no APScheduler integration.

### 6. Frontend presentation

`ResearchAssessmentPanel` on the symbol page displays API payloads only. Module and export
names use the `ResearchAssessment*` stem so `check:no-domain-logic` continues to forbid
`score*`, `recommend*`, `predict*`, trading, and order exports. No client-side research math.

## Consequences

- Operators can request and inspect research-only assessments with explicit coverage
  confidence and null probability confidence.
- Later calibration or actionable promotion requires a superseding ADR and evidence gate.
- Frontend and backend structural gates still block recommendation/trading surfaces.

## Explicitly out of scope

- Actionable recommendations, signals, alerts, buy/sell UI
- Non-null `probability_confidence` / calibration
- Promote research_only to actionable
- Order placement or transmission
- Scheduled research runs
- Chart signal overlays
- Second provider, OAuth/MFA/RBAC expansion (NAS packaging is Phase 7 / ADR-0008)

## Related documents

- [../overview.md](../overview.md)
- [../data-model.md](../data-model.md)
- [0005-phase-4-operator-auth.md](0005-phase-4-operator-auth.md)
- [0006-phase-5-daily-bar-charts.md](0006-phase-5-daily-bar-charts.md)
