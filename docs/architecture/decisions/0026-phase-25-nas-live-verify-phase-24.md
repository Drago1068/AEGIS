# ADR-0026: Phase 25 NAS Live Verification of Phase 24

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 24 added authenticated `GET /research/{symbol}/evidence-summary/export`. Phase 23
live-verified the interactive evidence-summary aggregate on the UGREEN NAS (arm64 native
build; host ports 18000/13000). Operators need a verified redeploy of current `main` that
includes the JSON export contract without expanding product capabilities.

## Decisions

### 1. Scope

Phase 25 is an **ops evidence gate**:

1. Deploy current revision (native `linux/arm64` on-NAS build remains acceptable).
2. Run `verify.ps1` / `verify.sh` successfully (ADR-0018 / ADR-0022 / ADR-0024 checks remain
   mandatory).
3. Additionally confirm:
   - Unauthenticated `GET .../evidence-summary/export` → **401**
   - Authenticated export → **200**, `Content-Disposition` includes `attachment`, body
     `state` = `research_only`, non-negative counts

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- Default-on automatic calibration
- Multi-horizon method changes
- Actionable promotion, recommendations, orders
- TLS live cutover

## Related documents

- [0024-phase-23-nas-live-verify-phase-22.md](0024-phase-23-nas-live-verify-phase-22.md)
- [0025-phase-24-evidence-summary-export.md](0025-phase-24-evidence-summary-export.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
