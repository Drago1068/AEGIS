# ADR-0038: Phase 37 NAS Live Verification of Phase 36

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 36 added authenticated
`GET /research/{symbol}/assessments/{id}/calibrations/export`. Phase 35 live-verified
outcome-labels export on the UGREEN NAS (arm64 native build; host ports 18000/13000).
Operators need a verified redeploy of current `main` that includes the calibrations export
contract without expanding product capabilities.

## Decisions

### 1. Scope

Phase 37 is an **ops evidence gate**:

1. Deploy current revision (native `linux/arm64` on-NAS build remains acceptable).
2. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
3. Additionally confirm:
   - Unauthenticated `GET .../assessments/{id}/calibrations/export` → **401**
   - Authenticated export (using latest assessment id when present, else id `1`) → **200**,
     `Content-Disposition` includes `attachment`, body is a JSON array (`[]` OK)

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- New calibration methods or horizons
- Default-on automatic calibration
- Actionable promotion, recommendations, orders
- TLS live cutover

## Related documents

- [0036-phase-35-nas-live-verify-phase-34.md](0036-phase-35-nas-live-verify-phase-34.md)
- [0037-phase-36-calibrations-export.md](0037-phase-36-calibrations-export.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
