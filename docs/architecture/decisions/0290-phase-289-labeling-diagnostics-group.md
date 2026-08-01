# ADR-0290: Phase 289 Labeling Diagnostics Group

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 283–288 elevated three separate research-only callouts in evidence-summary:

1. Tip not label-ready (forward-bar shortfall)
2. Labeled corpus freshness lag
3. Empty unlabeled label-ready scan

Live AAPL often shows all three at once, stacking three warn asides. Prefer a single
grouped "Labeling diagnostics" region that contains the existing callouts (no new API
scalars) so operators see one composition for labeling runway issues.

## Decisions

### 1. Group wrapper

When any of the three callout conditions is true,
``ResearchEvidenceSummarySection`` wraps those asides in a single
``evidence-labeling-diagnostics`` region with a research-only heading. Individual
callout testids and field contents remain unchanged.

### 2. Out of scope

New API scalars, inventing labels/closes, orders, removing fail-closed wording,
calibration default-on.

## Related documents

- [0289-phase-288-nas-live-verify-phase-287.md](0289-phase-288-nas-live-verify-phase-287.md)
- [0291-phase-290-nas-live-verify-phase-289.md](0291-phase-290-nas-live-verify-phase-289.md)
