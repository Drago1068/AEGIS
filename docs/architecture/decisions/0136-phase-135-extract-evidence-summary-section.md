# ADR-0136: Phase 135 Extract Evidence Summary Panel Section

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 123–133 modularized toolbar and the history/readiness/calibration result sections.
``ResearchAssessmentPanel.tsx`` still embeds a large evidence-summary diagnostics block
(counts, provenance, nested readiness, most-recent labeled fields, load-scan-labeled
control). Extracting that section continues the maintainability path without behavior
change.

## Decisions

### 1. Console

Extract the evidence-summary UI into ``ResearchEvidenceSummarySection.tsx`` (props:
evidenceSummary, pending, and handlers for mixed-filter / load-scan-labeled). Move
horizon-expand UI state into the section. Preserve existing ``data-testid`` contracts.
Add ``data-testid="evidence-summary-section"``. No API changes.

### 2. Out of scope

New evidence-summary math, default-on calibration, orders, ACME.

## Related documents

- [0134-phase-133-extract-probability-calibration-section.md](0134-phase-133-extract-probability-calibration-section.md)
- [0137-phase-136-nas-live-verify-phase-135.md](0137-phase-136-nas-live-verify-phase-135.md)
