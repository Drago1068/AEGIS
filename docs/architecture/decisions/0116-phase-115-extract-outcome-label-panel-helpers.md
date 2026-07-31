# ADR-0116: Phase 115 Extract Outcome-Label Panel Helpers Module

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 111 and 113 added exported helpers
(``resolveOutcomeLabelHistoryLoadKind``, ``formatOutcomeLabelActionAriaLabel``) inside
``ResearchAssessmentPanel.tsx``. Keeping pure helpers in the panel module grows the
component file and makes audits harder.

## Decisions

### 1. Console

Move those helpers into ``frontend/src/components/research-assessment-panel-helpers.ts``.
Panel and tests import from that module. No behavior change.

### 2. Out of scope

Broader panel splits, UX copy changes, default-on calibration, orders, ACME.

## Related documents

- [0112-phase-111-resolve-outcome-label-history-load-kind.md](0112-phase-111-resolve-outcome-label-history-load-kind.md)
- [0114-phase-113-outcome-label-action-aria-load-kind.md](0114-phase-113-outcome-label-action-aria-load-kind.md)
- [0117-phase-116-nas-live-verify-phase-115.md](0117-phase-116-nas-live-verify-phase-115.md)
