# ADR-0079: Phase 78 NAS Live Verification of Phase 77

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 77 added click-to-expand ``by_horizon.detail`` on evidence-summary mini-rows
(ADR-0078). Operators need a verified frontend redeploy on the UGREEN NAS under the lab TLS
profile.

## Decisions

### 1. Scope

Phase 78 is an **ops evidence gate** on the HTTPS lab profile:

1. Deploy current ``HEAD`` with the TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory,
   including Phases 75–76 nested readiness asserts).
3. Phase 77 UX is accepted via unit tests; live verify does not automate browser clicks.
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Related documents

- [0078-phase-77-horizon-detail-expand.md](0078-phase-77-horizon-detail-expand.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
