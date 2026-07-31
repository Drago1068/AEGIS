# ADR-0120: Phase 119 Calibration Action Chips Name Latest Explicitly

- Status: Accepted
- Date: 2026-07-30

## Context

Outcome-label compute/download chips now show load-kind (Phases 113/117). Calibration
compute/download still show bare ``({latest.id})`` without an explicit ``latest`` marker,
even though calibration always targets latest (Phase 103 note).

## Decisions

### 1. Console

When ``latest.id`` is set, show ``({id} · latest)`` on compute/download calibration id chips
and append `` (latest)`` to their accessible names via ``formatCalibrationActionAriaLabel`` /
``formatCalibrationActionIdChip``. Keep calibration targeting ``latest`` only. No API changes.

### 2. Out of scope

Changing calibration target away from latest, default-on calibration, orders, ACME.

## Related documents

- [0102-phase-101-compute-calibration-names-latest.md](0102-phase-101-compute-calibration-names-latest.md)
- [0118-phase-117-outcome-label-action-id-chip-load-kind.md](0118-phase-117-outcome-label-action-id-chip-load-kind.md)
- [0121-phase-120-nas-live-verify-phase-119.md](0121-phase-120-nas-live-verify-phase-119.md)
