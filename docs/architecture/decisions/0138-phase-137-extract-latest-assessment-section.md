# ADR-0138: Phase 137 Extract Latest Assessment Detail Panel Section

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 123–135 modularized toolbar and diagnostic/history sections.
``ResearchAssessmentPanel.tsx`` still embeds the latest-assessment detail block (state
caption, coverage/probability fields, component factors). Extracting that section
continues the maintainability path without behavior change.

## Decisions

### 1. Console

Extract the latest-assessment detail UI into ``ResearchLatestAssessmentSection.tsx``
(props: ``latest`` assessment). Preserve existing labels and formatting. Add
``data-testid="latest-assessment-section"``. Child history/readiness/calibration sections
remain siblings under the panel (not nested into this extract). No API changes.

### 2. Out of scope

New assessment math, default-on calibration, orders, ACME.

## Related documents

- [0136-phase-135-extract-evidence-summary-section.md](0136-phase-135-extract-evidence-summary-section.md)
- [0139-phase-138-nas-live-verify-phase-137.md](0139-phase-138-nas-live-verify-phase-137.md)
