# ADR-0104: Phase 103 Calibration Controls Note When Scan-Labeled Differs

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 99–101 name calibration download/compute with ``latest.id``. When the outcome-label
panel is on a scan-labeled assessment that differs from ``latest``, operators can still
miss that calibration actions always target latest.

## Decisions

### 1. Console

When ``outcomeLabelHistoryAssessmentId`` is set and differs from ``latest.id``, show a
short research-only note near the calibration controls:

- **Calibration actions use latest assessment {latest.id} (panel labels are for {loaded
  id}).**

No new API fields; do not invent calibration data.

### 2. Out of scope

Binding calibration to scan-labeled assessments, default-on calibration, orders, ACME.

## Related documents

- [0100-phase-99-calibrations-download-names-latest.md](0100-phase-99-calibrations-download-names-latest.md)
- [0102-phase-101-compute-calibration-names-latest.md](0102-phase-101-compute-calibration-names-latest.md)
- [0105-phase-104-nas-live-verify-phase-103.md](0105-phase-104-nas-live-verify-phase-103.md)
