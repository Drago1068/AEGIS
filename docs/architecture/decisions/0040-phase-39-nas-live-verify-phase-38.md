# ADR-0040: Phase 39 NAS Live Verification of Phase 38

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 38 added authenticated `GET /research/{symbol}/assessments/export`. Phase 37
live-verified calibrations export on the UGREEN NAS (arm64 native build; host ports
18000/13000). Operators need a verified redeploy of current `main` that includes the
assessments export contract without expanding product capabilities.

## Decisions

### 1. Scope

Phase 39 is an **ops evidence gate**:

1. Deploy current revision (native `linux/arm64` on-NAS build remains acceptable).
2. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
3. Additionally confirm:
   - Unauthenticated `GET .../assessments/export` → **401**
   - Authenticated export → **200**, `Content-Disposition` includes `attachment`,
     body is a JSON array (`[]` OK)

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- New assessment methods or horizons
- Default-on automatic calibration
- Actionable promotion, recommendations, orders
- TLS live cutover

## Related documents

- [0038-phase-37-nas-live-verify-phase-36.md](0038-phase-37-nas-live-verify-phase-36.md)
- [0039-phase-38-assessments-export.md](0039-phase-38-assessments-export.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
