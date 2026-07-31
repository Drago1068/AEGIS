# ADR-0122: Phase 121 Outcome-Label Backfill Names Refresh Target

- Status: Accepted
- Date: 2026-07-30

## Context

Compute/download outcome-label actions name the active assessment (Phases 89–117). Label
backfill still shows a bare button even though post-backfill history refresh uses
``activeOutcomeLabelAssessmentId`` when set.

## Decisions

### 1. Console

When ``activeOutcomeLabelAssessmentId`` is set, show the same id chip (via
``formatOutcomeLabelActionIdChip``) on **Backfill outcome labels**, and set an accessible
name that states the refresh target assessment (including load-kind when tracked). When
unset, keep the bare control. Does not change backfill API scope (still corpus-wide).

### 2. Out of scope

Changing backfill selection filters, default-on calibration, orders, ACME.

## Related documents

- [0118-phase-117-outcome-label-action-id-chip-load-kind.md](0118-phase-117-outcome-label-action-id-chip-load-kind.md)
- [0123-phase-122-nas-live-verify-phase-121.md](0123-phase-122-nas-live-verify-phase-121.md)
