# ADR-0140: Phase 139 Extract Backfill Status Banners

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 123–137 modularized the research assessment panel into toolbar and section
components. ``ResearchAssessmentPanel.tsx`` still embeds inline outcome-label and
assessment backfill summary banners. Extracting those banners finishes the small remaining
presentational surface without behavior change.

## Decisions

### 1. Console

Extract backfill status UI into ``ResearchBackfillStatusSection.tsx`` (props: optional
outcome-label and assessment backfill summaries). Preserve
``data-testid="outcome-label-backfill-summary"`` and
``data-testid="assessment-backfill-summary"``. Add
``data-testid="backfill-status-section"``. No API changes.

### 2. Out of scope

New backfill math, default-on calibration, orders, ACME.

## Related documents

- [0138-phase-137-extract-latest-assessment-section.md](0138-phase-137-extract-latest-assessment-section.md)
- [0141-phase-140-nas-live-verify-phase-139.md](0141-phase-140-nas-live-verify-phase-139.md)
