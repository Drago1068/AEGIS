# ADR-0130: Phase 129 Extract Assessment History Panel Section

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 123–127 modularized the action toolbar and outcome-label history section.
``ResearchAssessmentPanel.tsx`` still embeds the assessment history block (source filter,
empty states, history list). Extracting that section continues the maintainability path
without behavior change.

## Decisions

### 1. Console

Extract the assessment history UI into ``ResearchAssessmentHistorySection.tsx``. Move
shared ``formatAssessmentHistoryRow`` / ``ASSESSMENT_SOURCE_FILTER_OPTIONS`` into
``research-assessment-panel-helpers.ts`` (or keep options co-located with the section if
section-private). Preserve ``id="assessment-history"`` and existing filter/list behavior.
No API changes.

### 2. Out of scope

New assessment math, default-on calibration, orders, ACME.

## Related documents

- [0128-phase-127-extract-outcome-label-history-section.md](0128-phase-127-extract-outcome-label-history-section.md)
- [0131-phase-130-nas-live-verify-phase-129.md](0131-phase-130-nas-live-verify-phase-129.md)
