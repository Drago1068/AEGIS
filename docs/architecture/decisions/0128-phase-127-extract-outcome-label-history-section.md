# ADR-0128: Phase 127 Extract Outcome-Label History Panel Section

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 123–125 modularized the action toolbar. ``ResearchAssessmentPanel.tsx`` still embeds
a large outcome-label history block (caption, empty state, load-latest control, list).
Extracting that section continues the maintainability path without behavior change.

## Decisions

### 1. Console

Extract the outcome-label history UI into ``ResearchOutcomeLabelHistorySection.tsx``.
Move shared ``sortedLabelEntries`` / ``formatLabelHorizonSummary`` into
``research-assessment-panel-helpers.ts``. Preserve existing ``data-testid`` contracts.
``load-scan-labeled-labels`` remains in the evidence-summary block (co-located with
most-recent labeled fields). No API changes.

### 2. Out of scope

New outcome-label math, default-on calibration, orders, ACME.

## Related documents

- [0124-phase-123-extract-research-assessment-action-toolbar.md](0124-phase-123-extract-research-assessment-action-toolbar.md)
- [0129-phase-128-nas-live-verify-phase-127.md](0129-phase-128-nas-live-verify-phase-127.md)
