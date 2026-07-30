# ADR-0036: Phase 35 NAS Live Verification of Phase 34

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 34 added authenticated
`GET /research/{symbol}/assessments/{id}/outcome-labels/export`. Phase 33 live-verified
calibration-readiness export on the UGREEN NAS (arm64 native build; host ports 18000/13000).
Operators need a verified redeploy of current `main` that includes the outcome-labels export
contract without expanding product capabilities.

## Decisions

### 1. Scope

Phase 35 is an **ops evidence gate**:

1. Deploy current revision (native `linux/arm64` on-NAS build remains acceptable).
2. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
3. Additionally confirm:
   - Unauthenticated `GET .../assessments/{id}/outcome-labels/export` → **401**
   - Authenticated export (using latest assessment id when present, else id `1`) → **200**,
     `Content-Disposition` includes `attachment`, body is a JSON array (`[]` OK)

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- New label methods or horizons
- Default-on automatic calibration
- Actionable promotion, recommendations, orders
- TLS live cutover

## Related documents

- [0034-phase-33-nas-live-verify-phase-32.md](0034-phase-33-nas-live-verify-phase-32.md)
- [0035-phase-34-outcome-labels-export.md](0035-phase-34-outcome-labels-export.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
