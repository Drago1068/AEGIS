# ADR-0100: Phase 99 Calibrations Download Names Latest Assessment Id

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 87–97 bind outcome-label actions to a loaded assessment id that may differ from
``latest``. The calibrations download still always targets ``latest.id`` but the button
label does not say so, which can confuse operators after scan-labeled loads.

## Decisions

### 1. Console

When ``latest.id`` is set, the calibrations download control:

- Shows ``({latest.id})`` after the button text
- Sets ``aria-label`` to ``Download calibrations JSON for assessment {latest.id}``
- Exposes ``data-testid="download-calibrations"``

Calibrations remain tied to ``latest`` (not scan-labeled) in this phase.

### 2. Out of scope

Binding calibrations to scan-labeled assessments, new API fields, default-on calibration,
orders, ACME.

## Related documents

- [0090-phase-89-outcome-label-download-names-assessment.md](0090-phase-89-outcome-label-download-names-assessment.md)
- [0098-phase-97-assessment-backfill-preserves-loaded-labels.md](0098-phase-97-assessment-backfill-preserves-loaded-labels.md)
- [0101-phase-100-nas-live-verify-phase-99.md](0101-phase-100-nas-live-verify-phase-99.md)
