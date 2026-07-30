# ADR-0076: Phase 75 Evidence-Summary Nested by_horizon Verify Assertion

- Status: Accepted (live verified 2026-07-30 on ``46cc9e2``)
- Date: 2026-07-30

## Context

Phase 73 surfaces ``calibration_readiness.by_horizon`` on the evidence-summary console
(ADR-0074). Phase 74 live-verified the frontend redeploy (ADR-0075). Live verify already
asserts ``by_horizon`` on the dedicated calibration-readiness route (Phase 42) but not on
the nested readiness object inside authenticated evidence-summary (+ export). Operators need
that contract locked so Phase 73 UI does not silently lose horizon rows.

## Decisions

### 1. Scope

Phase 75 is an **ops hardening** gate (no product math):

1. Authenticated ``GET .../evidence-summary`` requires
   ``calibration_readiness.by_horizon`` with ``forward_return_5`` and ``forward_return_20``.
2. Authenticated ``GET .../evidence-summary/export`` requires the same nested keys.
3. Update `verify.ps1` / `verify.sh` checklist item; prior ADR checks remain mandatory.
4. Sync verify scripts to the NAS and run live verify successfully.
5. Calibration defaults remain off; no new API fields.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New readiness math, default-on calibration, ACME, actionable promotion, orders.

## Related documents

- [0074-phase-73-per-horizon-readiness-evidence-summary.md](0074-phase-73-per-horizon-readiness-evidence-summary.md)
- [0075-phase-74-nas-live-verify-phase-73.md](0075-phase-74-nas-live-verify-phase-73.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
