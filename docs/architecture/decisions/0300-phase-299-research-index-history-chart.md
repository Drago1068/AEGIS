# ADR-0300: Phase 299 Research Index History Chart (draft)

- Status: Proposed (Phase 298 closed; ready to implement after gate approval)
- Date: 2026-08-01

## Context

Phases 283–298 elevated labeling and fetch-fallback diagnostics. Live AAPL still
shows tip-not-ready (shortfall ``20`` until ``2026-08-28``), freshness lag ``121``,
and empty unlabeled-ready count — calendar-bound until forward bars arrive. Further
callout stacking adds little operator value.

``lightweight-charts`` is already a frontend dependency. Assessment history already
exposes ``research_index`` and ``as_of_trading_date`` via the list API. Operators lack
a research-only time series of research_index to see trend without opening each row.

## Decisions

### 1. Research-index history chart

Add a research-only chart (or sparkline) on the assessment panel fed from the existing
assessments list payload (``research_index`` vs ``as_of_trading_date``). Label clearly
as research-only / not advice. Fail closed on empty or non-finite points (skip; do not
invent). No new backend scalars unless a documented gap appears.

### 2. Out of scope

Live orders, actionable promotion, inventing assessments/labels, calibration
default-on, additional labeling callouts.

## Resume

```powershell
# Implement Phase 299 chart from assessments list; tests; commit+push; then:
# git archive HEAD → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0299-phase-298-nas-live-verify-phase-297.md](0299-phase-298-nas-live-verify-phase-297.md)
- [0301-phase-300-nas-live-verify-phase-299.md](0301-phase-300-nas-live-verify-phase-299.md)
