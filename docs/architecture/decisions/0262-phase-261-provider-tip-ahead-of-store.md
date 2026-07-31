# ADR-0262: Phase 261 Provider Tip Ahead of Store Tip

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 259–260 exposed ingest ``latest_trading_date``. Live AAPL showed provider tip
``2026-07-30`` while store / evidence tip stayed ``2026-07-29`` with ``stored=0`` and
``skipped_existing=501``. NAS inspection showed:

- ``alpha_vantage`` tip ``2026-07-29`` (label / assessment ``input_source``)
- ``polygon`` tip ``2026-07-30`` (failover / secondary history)
- Backend logs ``market_data_ingestion_failover``

Root causes:

1. **Ingest:** secondary was only fetched on primary failover, so a successful but lagging
   primary could hide a fresher secondary tip; failover attributed tip to polygon while
   label source remained alpha_vantage.
2. **Research:** with cross-source fill enabled, ``_select_component_bars`` short-circuited
   once primary had 20 sessions, so a newer secondary tip never advanced ``lookback_end``.

Prefer a fail-closed root-cause fix (never invent closes / never rewrite provenance).

## Decisions

### 1. Dual-source tip catch-up

When a secondary provider is configured, ingest refreshes **primary and secondary
independently** per symbol. Each write keeps the producing adapter's ``source`` (ADR-0011).
``latest_trading_date`` is the max tip across successful providers;
``latest_trading_date_source`` attributes that tip. One-sided provider failure is logged;
overall symbol success if either side stores/skips without error.

### 2. Cross-source fill extends stale primary tip

When ``allow_cross_source_component_fill`` is true, component selection always unions
primary and secondary session dates (prefer primary per date). A fresher secondary tip
advances ``lookback_end`` / ``as_of`` even when primary already has a full lookback.
Post-ingest research can then append a newer assessment so evidence tip / calendar lag
reflect stored secondary closes without inventing primary rows.

### 3. Out of scope

Inventing alpha_vantage closes from polygon, default-on calibration, orders, UI
modularization beyond tip-source attribution.

## Consequences

- ADR-0011 “secondary only on failover” is superseded for tip catch-up; provenance rules
  unchanged.
- Operators see tip source on ingest results / verify logs.
- Phase 262 NAS verifies tip advancement or explicit dual-source attribution.

## Resume (Phase 262)

```powershell
# git archive HEAD → NAS; rebuild backend(+frontend) TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0260-phase-259-ingest-run-latest-trading-date.md](0260-phase-259-ingest-run-latest-trading-date.md)
- [0261-phase-260-nas-live-verify-phase-259.md](0261-phase-260-nas-live-verify-phase-259.md)
- [0263-phase-262-nas-live-verify-phase-261.md](0263-phase-262-nas-live-verify-phase-261.md)
- [0011-phase-10-second-market-data-provider.md](0011-phase-10-second-market-data-provider.md)
- [0056-phase-55-research-cross-source-session-depth.md](0056-phase-55-research-cross-source-session-depth.md)
