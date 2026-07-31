# ADR-0118: Phase 117 Outcome-Label Action Id Chip Includes Load Kind

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 113 added load-kind to compute/download accessible names. Sighted operators still see
only ``({id})`` on the button chips and must read the caption for load-kind.

## Decisions

### 1. Console

When ``outcomeLabelHistoryLoadKind`` is set, show ``({id} · scan-labeled)`` or
``({id} · latest)`` on compute/download outcome-label id chips. When unset, keep ``({id})``.
Add ``formatOutcomeLabelActionIdChip`` in the helpers module. No API changes.

### 2. Out of scope

Calibration chip changes, default-on calibration, orders, ACME.

## Related documents

- [0114-phase-113-outcome-label-action-aria-load-kind.md](0114-phase-113-outcome-label-action-aria-load-kind.md)
- [0116-phase-115-extract-outcome-label-panel-helpers.md](0116-phase-115-extract-outcome-label-panel-helpers.md)
- [0119-phase-118-nas-live-verify-phase-117.md](0119-phase-118-nas-live-verify-phase-117.md)
