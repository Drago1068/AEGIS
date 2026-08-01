# ADR-0284: Phase 283 Latest Assessment Label-Readiness Callout (draft)

- Status: Proposed (ready after Phase 282; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 275–282 closed compact-fetch fallback diagnostics across ingest, evidence-summary,
and daily-bars (live primary ``full_to_compact``; multi-source bars tip may be polygon with
null fallback). A remaining product gap: the latest assessment is often not label-ready
(``insufficient_forward_bars``, shortfall ``20``, required end date weeks ahead) while
labeled corpus freshness lag remains large (``scan_labeled_freshness_lag_trading_days≈121``).
Operators already have the scalars in evidence-summary, but the research panel does not
elevate why the tip assessment cannot yet be labeled.

Prefer a fail-closed UI callout over more tip/fallback scalars or UI modularization.

## Decisions (proposed)

### 1. Label-readiness callout

When evidence-summary reports ``latest_assessment_is_label_ready=false``, surface a clear
research-only callout with existing fields only:

- ``latest_assessment_label_block_reason``
- ``latest_assessment_forward_bar_shortfall`` (and/or min-horizon shortfall)
- ``latest_assessment_required_label_end_date`` (and/or min-horizon end date)
- ``most_recent_labelable_as_of_trading_date`` when present

Never invent closes; never promote to actionable; no orders.

### 2. Out of scope

New tip/fallback scalars, inventing bars, calibration default-on, orders.

## Resume (after Phase 282 gate)

```powershell
# Surface latest label-readiness callout from evidence-summary fields (ADR-0284); tests; commit+push; then Phase 284:
# git archive HEAD → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0283-phase-282-nas-live-verify-phase-281.md](0283-phase-282-nas-live-verify-phase-281.md)
- [0285-phase-284-nas-live-verify-phase-283.md](0285-phase-284-nas-live-verify-phase-283.md)
