# ADR-0034: Phase 33 NAS Live Verification of Phase 32

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 32 added authenticated `GET /research/{symbol}/calibration-readiness/export`. Phase 31
live-verified the label end-date UI on the UGREEN NAS (arm64 native build; host ports
18000/13000). Operators need a verified redeploy of current `main` that includes the
readiness export contract without expanding product capabilities.

## Decisions

### 1. Scope

Phase 33 is an **ops evidence gate**:

1. Deploy current revision (native `linux/arm64` on-NAS build remains acceptable).
2. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
3. Additionally confirm:
   - Unauthenticated `GET .../calibration-readiness/export` → **401**
   - Authenticated export → **200**, `Content-Disposition` includes `attachment`, body
     includes readiness `status` (diagnostics only; no invented probability)

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- Default-on automatic calibration
- Horizon-specific calibration methods
- Actionable promotion, recommendations, orders
- TLS live cutover

## Related documents

- [0032-phase-31-nas-live-verify-phase-30.md](0032-phase-31-nas-live-verify-phase-30.md)
- [0033-phase-32-calibration-readiness-export.md](0033-phase-32-calibration-readiness-export.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
