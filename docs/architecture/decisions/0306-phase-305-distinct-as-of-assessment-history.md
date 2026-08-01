# ADR-0306: Phase 305 Distinct-as_of Assessment History

- Status: Accepted
- Date: 2026-08-01

## Context

Phases 299–304 charted research_index and coverage_confidence from the assessments
list (limit 100). Live lists still showed many rows sharing the same tip
``as_of_trading_date`` (repeated assess/calibrate), so the textual history was noisier
than the charts (which already dedupe by as_of). Further chart stacking adds little.

Prefer a research-only distinct-as_of presentation of the history list (newest row per
as_of), with an optional control to show all rows — no new API scalars.

## Decisions

### 1. Distinct-as_of history list

Default the assessment history list UI to one row per ``as_of_trading_date`` (newest
wins, matching chart dedupe) via ``distinctAsOfAssessments``. Keep a research-only
``Show all rows`` checkbox to reveal the full newest-first list. Charts remain fed by
the full list. Expose counts via ``assessment-history-as-of-counts`` and list mode via
``data-history-mode``. Fail closed: never invent rows; skip invalid dates.

### 2. Out of scope

Live orders, inventing assessments, deleting snapshots, additional charts, calibration
default-on.

## Related documents

- [0305-phase-304-nas-live-verify-phase-303.md](0305-phase-304-nas-live-verify-phase-303.md)
- [0307-phase-306-nas-live-verify-phase-305.md](0307-phase-306-nas-live-verify-phase-305.md)
