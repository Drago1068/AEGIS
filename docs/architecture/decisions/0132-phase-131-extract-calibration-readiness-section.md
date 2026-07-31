# ADR-0132: Phase 131 Extract Calibration Readiness Panel Section

- Status: Accepted (drafted; implement next)
- Date: 2026-07-30

## Context

Phases 123–129 modularized the action toolbar, outcome-label history, and assessment
history sections. ``ResearchAssessmentPanel.tsx`` still embeds the calibration readiness
diagnostics block. Extracting that section continues the maintainability path without
behavior change.

## Decisions

### 1. Console

Extract the calibration readiness UI into ``ResearchCalibrationReadinessSection.tsx``
(props: readiness object). Preserve existing labels and ``by_horizon`` list rendering.
No API changes.

### 2. Out of scope

New calibration math, default-on calibration, orders, ACME.

## Related documents

- [0130-phase-129-extract-assessment-history-section.md](0130-phase-129-extract-assessment-history-section.md)
- [0133-phase-132-nas-live-verify-phase-131.md](0133-phase-132-nas-live-verify-phase-131.md)
