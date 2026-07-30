# ADR-0024: Phase 23 NAS Live Verification of Phase 22

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 22 added authenticated `GET /research/{symbol}/evidence-summary`. Phase 21 live-verified
Phases 18–20 history routes on the UGREEN NAS (arm64 native build; host ports 18000/13000).
Operators need a verified redeploy of current `main` that includes the evidence-summary
contract without expanding product capabilities.

## Decisions

### 1. Scope

Phase 23 is an **ops evidence gate**:

1. Deploy current revision (native `linux/arm64` on-NAS build remains acceptable).
2. Run `verify.ps1` / `verify.sh` successfully (ADR-0018 / ADR-0022 checks remain mandatory).
3. Additionally confirm authenticated
   `GET /research/{symbol}/evidence-summary` returns **200** with:
   - `state` = `research_only`
   - non-negative counts
   - null/zero for missing pieces (never invent probability or labels)

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- Default-on automatic calibration
- Multi-horizon method changes
- Actionable promotion, recommendations, orders

## Related documents

- [0022-phase-21-nas-live-verify-phases-18-20.md](0022-phase-21-nas-live-verify-phases-18-20.md)
- [0023-phase-22-research-evidence-summary.md](0023-phase-22-research-evidence-summary.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
