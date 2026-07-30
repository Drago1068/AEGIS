# ADR-0030: Phase 29 NAS Live Verification of Phase 28

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 28 surfaced newest-first research assessment history in the operator console via
existing `GET /research/{symbol}/assessments?limit=`. Phase 27 live-verified the
multi-horizon UI revision on the UGREEN NAS (arm64 native build; host ports 18000/13000).
Operators need a verified redeploy of current `main` that includes the assessment-history
console without expanding product capabilities.

## Decisions

### 1. Scope

Phase 29 is an **ops evidence gate**:

1. Deploy current revision (native `linux/arm64` on-NAS build remains acceptable).
2. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
3. Additionally confirm:
   - Unauthenticated `GET /research/{symbol}/assessments` → **401**
   - Authenticated `GET /research/{symbol}/assessments?limit=20` → **200** JSON array
     (`[]` OK)

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- New assessment methods or horizons
- Horizon-specific calibration
- Default-on automatic calibration
- Actionable promotion, recommendations, orders
- TLS live cutover

## Related documents

- [0028-phase-27-nas-live-verify-phase-26.md](0028-phase-27-nas-live-verify-phase-26.md)
- [0029-phase-28-assessment-history-console.md](0029-phase-28-assessment-history-console.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
