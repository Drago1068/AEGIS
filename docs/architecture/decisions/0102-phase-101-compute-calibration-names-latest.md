# ADR-0102: Phase 101 Compute Calibration Names Latest Assessment Id

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 99 named the calibrations download with ``latest.id``. The compute-calibration control
also always targets ``latest`` but did not say so, which can confuse operators after
scan-labeled outcome-label loads.

## Decisions

### 1. Console

When ``latest.id`` is set, the compute-calibration control:

- Shows ``({latest.id})`` after the button text
- Sets ``aria-label`` to ``Compute calibration for assessment {latest.id}``
- Exposes ``data-testid="compute-calibration"``

Calibration remains tied to ``latest`` (not scan-labeled) in this phase.

### 2. Out of scope

Binding calibration compute to scan-labeled assessments, new API fields, default-on
calibration, orders, ACME.

## Related documents

- [0100-phase-99-calibrations-download-names-latest.md](0100-phase-99-calibrations-download-names-latest.md)
- [0090-phase-89-outcome-label-download-names-assessment.md](0090-phase-89-outcome-label-download-names-assessment.md)
