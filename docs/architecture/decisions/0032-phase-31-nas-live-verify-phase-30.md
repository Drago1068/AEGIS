# ADR-0032: Phase 31 NAS Live Verification of Phase 30

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 30 surfaced present `label_end_dates` in the operator console (display only). Phase 29
live-verified assessment history on the UGREEN NAS (arm64 native build; host ports
18000/13000). Operators need a verified redeploy of current `main` that includes the
end-date UI without expanding product capabilities.

## Decisions

### 1. Scope

Phase 31 is an **ops evidence gate**:

1. Deploy current revision (native `linux/arm64` on-NAS build remains acceptable).
2. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
3. When authenticated evidence-summary includes `latest_outcome_label`, log present
   `label_end_dates` keys only (never invent missing dates). Absence of labels remains OK.

Phase 30 is UI-only; scripted verify remains API/ops focused. Frontend reachability plus
successful image rebuild is packaging evidence for the console change.

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- New horizons or label methods
- Horizon-specific calibration
- Default-on automatic calibration
- Actionable promotion, recommendations, orders
- TLS live cutover

## Related documents

- [0030-phase-29-nas-live-verify-phase-28.md](0030-phase-29-nas-live-verify-phase-28.md)
- [0031-phase-30-label-end-date-surfacing.md](0031-phase-30-label-end-date-surfacing.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
