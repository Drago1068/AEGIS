# ADR-0112: Phase 111 Resolve Outcome-Label History Load Kind Helper

- Status: Accepted (drafted; implement next)
- Date: 2026-07-30

## Context

Compute and label-backfill refresh duplicate the load-kind resolution ternary
(``outcomeLabelHistoryLoadKind ?? (assessmentId === latest.id ? "latest" : "scan_labeled")``).
Phase 109 centralized the assessment id; load-kind resolution is the remaining drift risk.

## Decisions

### 1. Console

Extract a small ``resolveOutcomeLabelHistoryLoadKind(assessmentId)`` (or equivalent local
helper) used by ``onComputeOutcomeLabels`` and ``onBackfillOutcomeLabels``. Prefer reusing
it anywhere the same ternary appears without changing behavior.

### 2. Out of scope

New API fields, UX copy changes, default-on calibration, orders, ACME.

## Related documents

- [0110-phase-109-handlers-use-active-outcome-label-assessment-id.md](0110-phase-109-handlers-use-active-outcome-label-assessment-id.md)
- [0113-phase-112-nas-live-verify-phase-111.md](0113-phase-112-nas-live-verify-phase-111.md)
