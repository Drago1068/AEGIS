# ADR-0124: Phase 123 Extract Research Assessment Action Toolbar

- Status: Accepted (drafted; implement next)
- Date: 2026-07-30

## Context

``ResearchAssessmentPanel.tsx`` header action buttons grew through Phases 81–121 (load
labels, compute/download chips, calibration naming, backfill refresh naming). The panel
file is hard to review; extracting a presentational toolbar keeps behavior identical while
isolating control wiring.

## Decisions

### 1. Console

Extract the header action button cluster into a dedicated component such as
``ResearchAssessmentActionToolbar.tsx`` (props: pending flag, ids, load-kind, readiness
status, and click handlers). Keep helpers in ``research-assessment-panel-helpers.ts``.
No behavior or API changes.

### 2. Out of scope

UX regrouping/relabeling beyond extraction, default-on calibration, orders, ACME.

## Related documents

- [0116-phase-115-extract-outcome-label-panel-helpers.md](0116-phase-115-extract-outcome-label-panel-helpers.md)
- [0125-phase-124-nas-live-verify-phase-123.md](0125-phase-124-nas-live-verify-phase-123.md)
