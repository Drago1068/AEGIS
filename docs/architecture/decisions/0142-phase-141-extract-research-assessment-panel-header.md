# ADR-0142: Phase 141 Extract Research Assessment Panel Header

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 123–139 modularized toolbar, diagnostic sections, and backfill banners.
``ResearchAssessmentPanel.tsx`` still embeds the panel header copy (research-only eyebrow,
title, supporting sentence). Extracting that header completes the remaining static chrome
without behavior change.

## Decisions

### 1. Console

Extract header chrome into ``ResearchAssessmentPanelHeader.tsx`` accepting ``children`` for
the existing ``ResearchAssessmentActionToolbar``. Add
``data-testid="research-assessment-panel-header"``. Preserve copy and layout. No API
changes.

### 2. Out of scope

New product math, default-on calibration, orders, ACME.

## Related documents

- [0140-phase-139-extract-backfill-status-section.md](0140-phase-139-extract-backfill-status-section.md)
- [0143-phase-142-nas-live-verify-phase-141.md](0143-phase-142-nas-live-verify-phase-141.md)
