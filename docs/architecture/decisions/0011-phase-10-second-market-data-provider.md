# ADR-0011: Phase 10 Second Daily-Bar Market-Data Provider

- Status: Accepted
- Date: 2026-07-28

## Context

Phases 1–2 and 8 made scheduled ingest and post-ingest research depend on a single
Alpha Vantage free-tier adapter. Rate limits and premium gates abort symbol fetches and can
cascade into empty research cycles. ADR-0002 already anticipated a second adapter behind
`DailyBarProvider` with a distinct observation `source`. Phase 10 adds that adapter and a
config-driven primary/failover policy without calibration, actionable promotion, orders, or
auth changes.

## Decisions

### 1. Second provider: Polygon.io daily aggregates

The second concrete adapter is **Polygon.io** (API surface `https://api.polygon.io`) using
`GET /v2/aggs/ticker/{ticker}/range/1/day/{from}/{to}` (custom bars / daily aggregates).

| Concern | Choice |
| --- | --- |
| Source id stored on rows | `polygon` |
| Auth | API key via `Authorization: Bearer` (never logged; key not placed in query strings) |
| Adjustment | `adjusted=false` so bars align with Alpha Vantage unadjusted `TIME_SERIES_DAILY` |
| Lookback | Driven by existing `AEGIS_DAILY_BAR_OUTPUT_SIZE`: `compact` ≈ 160 calendar days; `full` ≈ 730 calendar days (Stocks Basic free-tier history is ~2 years — documented here, not assumed beyond that) |
| Trading date | Aggregate window start `t` (Unix ms) converted with `America/New_York`, matching Polygon’s ET session semantics |
| Empty `results` with `status=OK` | Valid empty list (no bars), not an error |
| HTTP 429 | `ProviderRateLimitError` |
| Transport / HTTP 5xx / missing API key | `ProviderUnavailableError` (failover-eligible) |
| Malformed / ERROR status / client 4xx (non-429) | `ProviderError` (no failover) |

Alpha Vantage remains a first-class adapter with source id `alpha_vantage` and may be
configured as primary or secondary.

**API notes at implement time:** Polygon documentation also references the Massive brand and
occasional `api.massive.com` hosts in samples. AEGIS defaults to `https://api.polygon.io` and
allows override via `AEGIS_POLYGON_BASE_URL`. Pagination via `next_url` is not followed in
Phase 10; compact/full windows fit a single page under the default `limit`.

### 2. Source identifiers

| Adapter | `source` value |
| --- | --- |
| Alpha Vantage | `alpha_vantage` |
| Polygon | `polygon` |

Uniqueness remains `(source, symbol, event_time)` on `market_daily_bar_observations`.
Re-ingest is still `ON CONFLICT DO NOTHING`. Failover never rewrites another source’s rows
and never silently stores under a different `source` than the adapter that produced the bars.

### 3. Primary selection and optional failover

| Setting | Role |
| --- | --- |
| `AEGIS_DAILY_BAR_PRIMARY_SOURCE` | Required; `alpha_vantage` (default) or `polygon` |
| `AEGIS_DAILY_BAR_SECONDARY_SOURCE` | Optional; other source id, or unset/empty for no failover |
| Per-provider API keys / base URLs / request intervals | Independent; placeholders only in `.env.example` / `.env.nas.example` |

**Per-symbol policy (deterministic):**

1. Fetch with the primary adapter.
2. On success, validate and persist with the primary’s `source`.
3. On `ProviderRateLimitError` or `ProviderUnavailableError`, if a secondary is configured,
   log a structured failover event and fetch once with the secondary.
4. On secondary success, validate and persist with the secondary’s `source`.
5. On secondary failure, or on non-failover `ProviderError` from primary, fail closed for that
   symbol (record error; continue other symbols). Do not invent blended bars.

**Non-failover `ProviderError` examples:** invalid symbol / coherent provider error body,
malformed bar payloads, missing time-series / ERROR status without rate-limit semantics.

Secondary equal to primary is a configuration error (settings validation fails closed).
Missing secondary key fails only when secondary is selected and invoked.

### 4. Research and labeling

Research method `daily_bar_research_v1` is unchanged. It still uses stored bars with
`data_quality=primary`, fail-closed gates, and `probability_confidence=null`.
`input_source` continues to reflect the bar `source` value(s) in the assessment window.
Multi-source consensus / blended bars remain out of scope; operators may accumulate parallel
histories under different `source` values when failover fires.

### 5. Explicitly out of scope

- Probability calibration / non-null `probability_confidence`
- Actionable promotion, recommendations, chart signals, orders
- Provider-side historical corrections
- Intraday / realtime quotes
- Multi-source consensus scoring or blended bars
- OAuth / MFA / RBAC
- Live NAS deployment from this phase
- Weakening quote validation or Secure-cookie / TLS posture

## Consequences

- Scheduled and on-demand ingest share one wiring path (DI + scheduler) that builds primary
  and optional secondary adapters from settings.
- Adding a third provider later is another adapter + source id + settings enum extension,
  not a domain rewrite.
- Operators should treat failover as resilience, not as silent equivalence of vendor bars.

## Related documents

- [0002-phase-1-market-data-ingestion.md](0002-phase-1-market-data-ingestion.md)
- [../overview.md](../overview.md)
- [../market-data-contracts.md](../market-data-contracts.md)
- [../../operations/configuration.md](../../operations/configuration.md)
