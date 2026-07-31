# ADR-0126: Phase 125 Group Research Assessment Action Toolbar

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 123 extracted the action toolbar without regrouping. The flat button row mixes
diagnostics, assessments, outcome labels, and calibration controls, which is hard to scan.

## Decisions

### 1. Console

Within ``ResearchAssessmentActionToolbar``, wrap related buttons in labeled groups with
muted section labels (not cards):

- Diagnostics
- Assessments
- Outcome labels
- Calibration
- (primary) Run assessment stays last without a group label

Preserve all existing ``data-testid`` values and handlers. No API changes.

### 2. Out of scope

Default-on calibration, changing action semantics, orders, ACME.

## Related documents

- [0124-phase-123-extract-research-assessment-action-toolbar.md](0124-phase-123-extract-research-assessment-action-toolbar.md)
- [0127-phase-126-nas-live-verify-phase-125.md](0127-phase-126-nas-live-verify-phase-125.md)
