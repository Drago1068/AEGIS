# ADR-0286: Phase 285 Labeled Corpus Freshness Lag Callout

- Status: Proposed (Phase 284 closed; ready to implement)
- Date: 2026-07-31

## Context

Phase 283–284 elevated tip label-readiness (``insufficient_forward_bars``, shortfall
``20``). Live verify also shows ``scan_labeled_freshness_lag_trading_days=121`` with
most recent labeled ``as_of`` ``2026-02-05`` while tip ``as_of`` is ``2026-07-31``.
Operators already have the scalars in evidence-summary, but the research panel does not
elevate how stale the labeled corpus is relative to the tip.

Prefer a fail-closed UI callout over new tip/fallback scalars.

## Decisions

### 1. Freshness-lag callout

When ``scan_labeled_freshness_lag_trading_days`` is a positive integer,
``ResearchEvidenceSummarySection`` shows a research-only callout with existing fields
only:

- ``scan_labeled_freshness_lag_trading_days``
- ``most_recent_labeled_outcome_label_as_of_trading_date`` when present
- ``most_recent_labelable_as_of_trading_date`` when present
- ``latest_as_of_trading_date`` when present (tip contrast)

Hidden when lag is null or ``<= 0``. Never invent labels; never promote to actionable;
no orders.

### 2. Out of scope

New API scalars, auto-labeling, inventing closes, orders, calibration default-on.

## Related documents

- [0285-phase-284-nas-live-verify-phase-283.md](0285-phase-284-nas-live-verify-phase-283.md)
- [0287-phase-286-nas-live-verify-phase-285.md](0287-phase-286-nas-live-verify-phase-285.md)
