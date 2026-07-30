# ADR-0075: Phase 74 NAS Live Verification of Phase 73

- Status: Accepted (live verified 2026-07-30; frontend recreate of ``99807af``+)
- Date: 2026-07-30

## Context

Phase 73 added evidence-summary “Readiness by horizon” mini-rows from nested
``calibration_readiness.by_horizon`` (ADR-0074). Operators need a verified frontend
redeploy on the UGREEN NAS under the lab TLS profile.

## Decisions

### 1. Scope

Phase 74 is an **ops evidence gate** on the HTTPS lab profile:

1. Deploy current ``HEAD`` (``99807af``+) with the TLS overlay; recreate **frontend**
   (backend optional if already on ``94cf550``+).
2. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
3. Phase 73 UX is accepted via unit tests; live verify does not automate browser clicks.
4. Evidence-summary authenticated response retains nested readiness ``by_horizon`` when the
   readiness endpoint would include it (already covered by calibration-readiness checks).
5. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Related documents

- [0074-phase-73-per-horizon-readiness-evidence-summary.md](0074-phase-73-per-horizon-readiness-evidence-summary.md)
- [0073-phase-72-nas-live-verify-phase-71.md](0073-phase-72-nas-live-verify-phase-71.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
