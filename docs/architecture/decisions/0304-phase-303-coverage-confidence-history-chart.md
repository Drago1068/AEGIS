# ADR-0304: Phase 303 Coverage Confidence History Chart (draft)

- Status: Proposed (Phase 302 closed; ready to implement after gate approval)
- Date: 2026-08-01

## Context

Phases 299–302 delivered a research-index history chart with denser ``limit=100``
series (live ``chartable_points=77``). Operators still lack a parallel research-only
view of ``coverage_confidence`` over ``as_of_trading_date`` — coverage is distinct
from probability confidence and from research_index, and must stay labeled as such.

Prefer reusing the same assessments list payload and fail-closed adapter pattern
(no new API scalars).

## Decisions

### 1. Coverage-confidence history chart

Add a research-only chart (or second series) of ``coverage_confidence`` vs
``as_of_trading_date`` from the assessments list, adjacent to the research_index
chart. Keep coverage vs probability labeling explicit. Skip empty/non-finite points;
dedupe colliding as_of by newest row. No new backend scalars.

### 2. Out of scope

Live orders, inventing assessments, merging coverage into probability, calibration
default-on, additional labeling callouts.

## Resume

```powershell
# Implement Phase 303 coverage-confidence chart; tests; commit+push; then:
# git archive HEAD → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0303-phase-302-nas-live-verify-phase-301.md](0303-phase-302-nas-live-verify-phase-301.md)
- [0305-phase-304-nas-live-verify-phase-303.md](0305-phase-304-nas-live-verify-phase-303.md)
