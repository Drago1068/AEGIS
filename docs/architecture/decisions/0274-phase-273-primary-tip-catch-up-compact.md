# ADR-0274: Phase 273 Primary Tip Catch-Up When Full Output Is Premium-Gated

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 269–272 closed Polygon tip catch-up (``/prev``) and truthful lag=0 display. Live
AAPL still showed ``primary_latest_trading_date=2026-07-29`` while polygon tip was
``2026-07-31``. Alpha Vantage ``outputsize=full`` is premium-gated on free keys, so the
primary fetch failed and only the stored primary tip surfaced (ADR-0266) even when
``compact`` daily history would expose newer real AV closes.

Prefer a fail-closed compact retry with labeled provenance over inventing primary bars
from polygon.

## Decisions

### 1. Compact fallback on full gate

When ``daily_bar_output_size=full`` and Alpha Vantage raises ``ProviderRateLimitError``
(premium gate or throttle), ``AlphaVantageProvider`` retries once with ``compact``.
Successful compact bars keep ``source=alpha_vantage`` and add audit labels in
``raw_payload``:

- ``aegis_output_size=compact``
- ``aegis_fetch_fallback=full_to_compact``

If compact also fails, the original rate-limit error path remains (secondary / stored
primary tip fallback unchanged). Never copy polygon closes onto alpha_vantage.

### 2. Out of scope

Inventing closes, silent provenance swaps, default-on calibration, orders.

## Consequences

- Primary tip can advance with real AV compact closes when full is gated.
- Operators can audit fallback via stored ``raw_payload`` labels and structured logs.
- Phase 274 live-verifies under lab TLS.

## Related documents

- [0273-phase-272-nas-live-verify-phase-271.md](0273-phase-272-nas-live-verify-phase-271.md)
- [0275-phase-274-nas-live-verify-phase-273.md](0275-phase-274-nas-live-verify-phase-273.md)
- [0266-phase-265-stored-primary-tip-fallback.md](0266-phase-265-stored-primary-tip-fallback.md)
- [0002-phase-1-market-data-foundation.md](0002-phase-1-market-data-foundation.md)
