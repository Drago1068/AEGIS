# ADR-0012: Phase 11 Multi-Source Coverage Weighting (Research-Only)

- Status: Accepted
- Date: 2026-07-28

## Context

Phase 10 introduced a second daily-bar provider (`polygon`) with distinct observation
`source` values alongside `alpha_vantage`. Research method `daily_bar_research_v1`
(ADR-0007 / ADR-0009) still computed coverage from a single Phase 6 product of bar-count,
freshness, and primary-fraction factors, and selected component bars by `data_quality`
without preferring a configured source.

Phase 11 extends **research-only** `coverage_confidence` with multi-source availability and
agreement factors when multiple configured research sources have usable bars in the lookback
window. It must not blend OHLCV, calibrate probabilities, promote to actionable, or place
orders.

## Decisions

### 1. Method identity and version

- `method_id` remains `daily_bar_research_v1`.
- `method_version = 2` when multi-source coverage weighting is enabled and applied.
- When `AEGIS_RESEARCH_MULTI_SOURCE_COVERAGE_ENABLED=false`, preserve Phase 6
  `method_version = 1` behavior and formula (feature flag off path).
- `schema_version = 2` for v2 snapshots so components JSON may carry non-numeric provenance
  and factor breakdown fields. v1 snapshots remain `schema_version = 1` with numeric-only
  component keys.

### 2. Component series source selection (no OHLCV blend)

Return / realized-vol / research-index use a **single preferred source** series:

1. Prefer usable `data_quality=primary` bars from `AEGIS_DAILY_BAR_PRIMARY_SOURCE`.
2. Cross-source fill from `AEGIS_DAILY_BAR_SECONDARY_SOURCE` is allowed **only** when
   `AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL=true`. Phase 11 shipped default
   **false**; Phase 55 / ADR-0056 changes the default to **true** so deep secondary
   history can grow research corpora when primary compact lookback is shallow (still
   overridable to false for primary-only labs).
3. When fill is disabled: fewer than 20 usable primary-source bars →
   `insufficient_primary_bars` (no stitching across sources).
4. When fill is enabled, each lookback date prefers primary if present, else secondary;
   never invent or average OHLCV. `component_source` is the single source id when uniform,
   or `mixed` when both contribute.

### 3. Coverage formula (method_version 2)

```
bar_count_factor            = min(1, usable_component_primary_bars / 20)
primary_fraction           = usable_component_primary_bars / total_component_source_bars_in_window
freshness_factor           = (unchanged from ADR-0007)
source_availability_factor = dates_with_any_configured_usable / expected_trading_dates_in_window
source_agreement_factor    = agreeing_dates / comparable_dates
                             if comparable_dates > 0; else 1
coverage_confidence        = clip_[0,1](
  bar_count_factor * freshness_factor * primary_fraction
  * source_availability_factor * source_agreement_factor
)
```

Clarifications:

- **Component-scoped primary_fraction**: denominator counts bars of the component source(s)
  used for the series in the lookback date range (not every vendor row), so a healthy
  dual-source install is not spuriously halved solely because two sources coexist.
- **Expected trading dates**: exchange sessions from `lookback_start` through `lookback_end`
  inclusive (calendar named by `AEGIS_EXCHANGE_CALENDAR_NAME`).
- **Configured research sources**: `AEGIS_DAILY_BAR_PRIMARY_SOURCE` plus optional
  `AEGIS_DAILY_BAR_SECONDARY_SOURCE` when set.
- **Usable bar**: same OHLCV usability rules as Phase 6; coverage availability also requires
  `data_quality=primary`.
- **Comparable date**: a lookback session date with usable primary closes from **≥2**
  configured sources. Closes **agree** when
  `(max(closes) - min(closes)) / max(closes) <= AEGIS_RESEARCH_MULTI_SOURCE_CLOSE_TOLERANCE`
  (default `0.002`).
- **Single-source installs**: `comparable_dates == 0` ⇒ `source_agreement_factor = 1`
  (must not tank coverage).

`probability_confidence` remains `null`. `state` remains `research_only`. The two
confidences are never merged.

### 4. Optional disagreement hard reject

When `AEGIS_RESEARCH_MULTI_SOURCE_DISAGREEMENT_FAIL_CLOSED=true` and
`comparable_dates > 0` and `source_agreement_factor < 0.80` (documented floor
`MULTI_SOURCE_AGREEMENT_FLOOR`), fail closed with reason `multi_source_disagreement` and
persist nothing. When the flag is false (default), only the soft product penalty applies.

### 5. Feature flag

`AEGIS_RESEARCH_MULTI_SOURCE_COVERAGE_ENABLED` (example default `true`):

| Value | Behavior |
| --- | --- |
| `true` | method_version 2, schema_version 2, preferred-source components, multi-source factors |
| `false` | Phase 6 path: method_version 1, schema_version 1, any-source primary-quality selection, three-factor coverage only |

### 6. Provenance (components JSON / API)

v2 components include research metrics plus:

- `component_source`, `coverage_sources`
- `comparable_dates`, `agreeing_dates`
- factor breakdown: `bar_count_factor`, `freshness_factor`, `primary_fraction`,
  `source_availability_factor`, `source_agreement_factor`

Presentation-only in the operator console; no client-side research math.

### 7. Fail-closed gates

At least as strict as Phase 6 / 8:

- insufficient preferred-source (or fill-enabled) usable bars
- unusable OHLCV on selected component bars
- stale latest bar vs exchange calendar
- optional multi-source disagreement floor (above)

No blended bars, corrections, orders, or actionable promotion.

## Consequences

- Operators with dual histories get transparent availability/agreement penalties without
  inventing consensus OHLCV.
- Disabling the feature flag restores Phase 6 snapshot shape for operators who want v1
  continuity.
- Calibration and blended bars remain future ADRs.

## Explicitly out of scope

- Non-null `probability_confidence` / calibration
- Blended or consensus OHLCV bars
- Historical corrections / overwrite
- Actionable promotion, recommendations, orders
- Live network in CI; live NAS deploy from this phase

## Related documents

- [0007-phase-6-research-only-scoring.md](0007-phase-6-research-only-scoring.md)
- [0009-phase-8-scheduled-research.md](0009-phase-8-scheduled-research.md)
- [0011-phase-10-second-market-data-provider.md](0011-phase-10-second-market-data-provider.md)
- [../overview.md](../overview.md)
- [../../operations/configuration.md](../../operations/configuration.md)
