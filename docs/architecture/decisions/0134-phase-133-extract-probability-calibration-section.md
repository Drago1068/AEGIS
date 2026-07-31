# ADR-0134: Phase 133 Extract Probability Calibration Panel Section

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 123–131 modularized toolbar, outcome-label history, assessment history, and
calibration readiness. ``ResearchAssessmentPanel.tsx`` still embeds the probability
calibration result block (fields + history list). Extracting that section continues the
maintainability path without behavior change.

## Decisions

### 1. Console

Extract the probability calibration UI into ``ResearchProbabilityCalibrationSection.tsx``
(props: calibration, calibrationHistory). Preserve existing labels and history list.
Add ``data-testid="probability-calibration-section"``. No API changes.

### 2. Out of scope

New calibration math, default-on calibration, orders, ACME.

## Related documents

- [0132-phase-131-extract-calibration-readiness-section.md](0132-phase-131-extract-calibration-readiness-section.md)
- [0135-phase-134-nas-live-verify-phase-133.md](0135-phase-134-nas-live-verify-phase-133.md)
