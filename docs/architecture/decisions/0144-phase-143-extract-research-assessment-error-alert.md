# ADR-0144: Phase 143 Extract Research Assessment Error Alert

- Status: Accepted (drafted; implement next)
- Date: 2026-07-30

## Context

Phases 123–141 modularized the research assessment panel into header, toolbar, and
section components. The panel still embeds a small inline error ``role="alert"`` banner.
Extracting it finishes the last presentational chrome without behavior change.

## Decisions

### 1. Console

Extract the error alert into ``ResearchAssessmentErrorAlert.tsx`` (props: ``error`` string
or null; render nothing when null). Preserve ``role="alert"``. Add
``data-testid="research-assessment-error"``. No API changes.

### 2. Out of scope

New product math, default-on calibration, orders, ACME. After this extract, further panel
UI modularization is complete; next work should prefer product/evidence improvements over
additional structural extracts.

## Related documents

- [0142-phase-141-extract-research-assessment-panel-header.md](0142-phase-141-extract-research-assessment-panel-header.md)
- [0145-phase-144-nas-live-verify-phase-143.md](0145-phase-144-nas-live-verify-phase-143.md)
