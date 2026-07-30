# ADR-0054: Phase 53 Full Daily-Bar History for Research Corpus Growth

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 51 raised ``AEGIS_RESEARCH_BAR_LOAD_LIMIT`` to 252, but live Phase 52 verify still
saw a saturated corpus under ``AEGIS_DAILY_BAR_OUTPUT_SIZE=compact`` (≈100 Alpha Vantage
bars). Deeper research loads cannot invent bars that were never ingested. Operators need
``full`` history as the supported default for research-capable deploys while keeping
``compact`` available for light labs.

## Decisions

### 1. Default lookback

Change ``daily_bar_output_size`` default from ``compact`` to **``full``**:

- Alpha Vantage: ``outputsize=full`` (full available daily history).
- Polygon: existing ADR-0011 ``full`` calendar-day window (~730 days).

``compact`` remains a valid explicit setting for rate-limit-sensitive or storage-light labs.

### 2. Compose pass-through

Wire ``AEGIS_DAILY_BAR_OUTPUT_SIZE`` into backend environment in ``docker-compose.yml`` and
the NAS overlay (same pattern as Phase 52 bar-load wiring) so ``.env`` / ``.env.nas`` values
reach the container.

### 3. Operator re-ingest

Switching an existing deployment from ``compact`` to ``full`` does **not** rewrite history
automatically. Operators must re-run ingest (scheduled or on-demand
``POST /market-data/ingest``) after changing the setting and recreating the backend so
append-only storage can grow with newly fetched older bars. Documented in configuration /
ops notes; this phase does not add a dedicated backfill job.

### 4. Out of scope

- Guaranteeing calibration readiness ``ready``
- Automatic correction/history rebuild jobs
- Default-on calibration
- Actionable promotion, recommendations, orders
- ACME / public TLS

## Related documents

- [0052-phase-51-research-bar-load-limit.md](0052-phase-51-research-bar-load-limit.md)
- [0053-phase-52-nas-live-verify-phase-51.md](0053-phase-52-nas-live-verify-phase-51.md)
- [0011-phase-10-second-market-data-provider.md](0011-phase-10-second-market-data-provider.md)
- [../../operations/configuration.md](../../operations/configuration.md)
