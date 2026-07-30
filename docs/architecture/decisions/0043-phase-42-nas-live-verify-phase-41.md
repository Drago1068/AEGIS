# ADR-0043: Phase 42 NAS Live Verification of Phase 41

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 41 added horizon-specific probability calibration (`outcome_horizon_key`, readiness
`by_horizon`, `POST .../calibrations?horizon=`). Phase 40 enabled the lab TLS profile on the
UGREEN NAS. Operators need a verified redeploy of current `main` that includes migration
`0009` and multi-horizon readiness diagnostics without expanding product capabilities.

## Decisions

### 1. Scope

Phase 42 is an **ops evidence gate** on the HTTPS lab profile:

1. Deploy current revision with the TLS overlay (native `linux/arm64` acceptable).
2. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
3. Additionally confirm:
   - SSH `alembic current` includes **`0009`** or `head`
   - Authenticated calibration-readiness (and export) include `by_horizon` entries for
     `forward_return_5` and `forward_return_20` (status values may be non-ready)
   - Optional: authenticated `POST .../calibrations?horizon=forward_return_5` returns
     **200** or **422** (fail-closed corpus thin is OK; never invent confidence)

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- ACME / public DNS
- New horizons beyond 5/20
- Default-on automatic calibration
- Actionable promotion, recommendations, orders

## Related documents

- [0041-phase-40-nas-lab-tls-cutover.md](0041-phase-40-nas-lab-tls-cutover.md)
- [0042-phase-41-multi-horizon-calibration.md](0042-phase-41-multi-horizon-calibration.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
- [../../operations/nas-tls-cutover.md](../../operations/nas-tls-cutover.md)
