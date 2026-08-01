# ADR-0304: Phase 303 Coverage Confidence History Chart

- Status: Accepted
- Date: 2026-08-01

## Context

Phases 299–302 delivered a research-index history chart with denser ``limit=100``
series (live ``chartable_points=77``). Operators lacked a parallel research-only
view of ``coverage_confidence`` over ``as_of_trading_date`` — coverage is distinct
from probability confidence and from research_index, and must stay labeled as such.

Prefer reusing the same assessments list payload and fail-closed adapter pattern
(no new API scalars).

## Decisions

### 1. Coverage-confidence history chart

Add a research-only line chart adjacent to the research_index chart, fed from
``coverage_confidence`` vs ``as_of_trading_date`` on the assessments list. Label
explicitly as distinct from probability confidence. Skip empty/non-finite points;
dedupe colliding as_of by newest row. Adapter:
``toCoverageConfidenceHistoryChartData``; UI: ``coverage-confidence-history-chart``.
Never invent coverage from ``probability_confidence``.

### 2. Out of scope

Live orders, inventing assessments, merging coverage into probability, calibration
default-on, additional labeling callouts.

## Related documents

- [0303-phase-302-nas-live-verify-phase-301.md](0303-phase-302-nas-live-verify-phase-301.md)
- [0305-phase-304-nas-live-verify-phase-303.md](0305-phase-304-nas-live-verify-phase-303.md)
