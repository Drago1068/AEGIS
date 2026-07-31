# ADR-0110: Phase 109 Handlers Use Active Outcome-Label Assessment Id

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 107 renamed the shared UI helper to ``activeOutcomeLabelAssessmentId`` but compute,
download, and label-backfill refresh handlers still re-derived
``outcomeLabelHistoryAssessmentId ?? latest?.id ?? null`` inline. That duplicates the
contract and risks drift.

## Decisions

### 1. Console

Move ``activeOutcomeLabelAssessmentId`` above the outcome-label action handlers and use it
as the single source of truth in:

- ``onComputeOutcomeLabels``
- ``onDownloadOutcomeLabels``
- ``onBackfillOutcomeLabels`` (post-backfill history refresh)

Do not change ``onBackfillAssessments`` (it intentionally tracks history id across a
``latest`` refresh). No operator-visible behavior change.

### 2. Out of scope

New API fields, UX copy changes, default-on calibration, orders, ACME.

## Related documents

- [0108-phase-107-rename-active-outcome-label-assessment-id.md](0108-phase-107-rename-active-outcome-label-assessment-id.md)
- [0111-phase-110-nas-live-verify-phase-109.md](0111-phase-110-nas-live-verify-phase-109.md)
