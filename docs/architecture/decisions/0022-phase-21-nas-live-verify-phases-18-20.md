# ADR-0022: Phase 21 NAS Live Verification of Phases 18–20

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 17 defined the live-verify evidence gate. Phase 18 added on-demand calibration; Phases
19–20 added append-only calibration and outcome-label history list routes. The UGREEN NAS
was previously live-verified for an earlier revision (arm64 native build; host ports
18000/13000). Operators need a verified redeploy of current `main` that includes history
endpoints without expanding product capabilities.

## Decisions

### 1. Scope

Phase 21 is an **ops evidence gate** for Phases 18–20 on the live NAS:

1. Deploy current revision (native `linux/arm64` build on aarch64 NAS is acceptable when
   workstation cross-build is impractical).
2. Run `verify.ps1` / `verify.sh` successfully (ADR-0018 checks remain mandatory).
3. Additionally confirm authenticated history routes return **200** with a JSON array:
   - `GET /research/{symbol}/assessments/{id}/calibrations`
   - `GET /research/{symbol}/assessments/{id}/outcome-labels`
   Empty `[]` is valid when no rows exist; do not invent probabilities or labels.

### 2. Upload ≠ verified

Package upload, native build, or `compose up` alone is still not acceptance. Retain live
verify stdout as evidence.

### 3. Out of scope

- Default-on automatic calibration
- Multi-horizon method changes
- Actionable promotion, recommendations, orders
- Changing research math

## Consequences

- Live stack matches Phases 18–20 contracts including history lists.
- Arm64 / alternate host ports remain documented operational adaptations, not product
  capability changes.

## Related documents

- [0018-phase-17-nas-live-verification.md](0018-phase-17-nas-live-verification.md)
- [0019-phase-18-on-demand-calibration.md](0019-phase-18-on-demand-calibration.md)
- [0020-phase-19-calibration-history.md](0020-phase-19-calibration-history.md)
- [0021-phase-20-outcome-label-history.md](0021-phase-20-outcome-label-history.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
