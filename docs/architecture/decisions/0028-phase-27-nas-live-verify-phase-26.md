# ADR-0028: Phase 27 NAS Live Verification of Phase 26

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 26 surfaced all present outcome-label horizon keys in the operator console (display
only; no API or method changes). Phase 25 live-verified the evidence-summary export on the
UGREEN NAS (arm64 native build; host ports 18000/13000). Operators need a verified redeploy
of current `main` that includes the Phase 26 frontend without expanding product
capabilities.

## Decisions

### 1. Scope

Phase 27 is an **ops evidence gate**:

1. Deploy current revision (native `linux/arm64` on-NAS build remains acceptable).
2. Run `verify.ps1` / `verify.sh` successfully (ADR-0018 through ADR-0026 checks remain
   mandatory).
3. Confirm authenticated `GET /research/{symbol}/evidence-summary` still returns
   `state=research_only`. When `latest_outcome_label` is present, log present `labels` keys
   only (never invent missing horizons).

Phase 26 is UI-only; scripted verify remains API/ops focused. Frontend reachability (existing
check) plus successful image rebuild is the packaging evidence for the console change.

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- New horizons or label methods
- Horizon-specific calibration
- Default-on automatic calibration
- Actionable promotion, recommendations, orders
- TLS live cutover

## Related documents

- [0026-phase-25-nas-live-verify-phase-24.md](0026-phase-25-nas-live-verify-phase-24.md)
- [0027-phase-26-multi-horizon-label-surfacing.md](0027-phase-26-multi-horizon-label-surfacing.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
