# ADR-0047: Phase 46 NAS Live Verification of Phase 45

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 45 added research-only historical assessment backfill
(`POST /research/{symbol}/assessments/backfill`). Operators need a verified redeploy of that
revision on the UGREEN NAS under the lab TLS profile without expanding product capabilities.

## Decisions

### 1. Scope

Phase 46 is an **ops evidence gate** on the HTTPS lab profile:

1. Deploy current revision with the TLS overlay (native `linux/arm64` acceptable).
2. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
3. Additionally confirm:
   - Unauthenticated `POST .../assessments/backfill` → **401**
   - Authenticated `POST .../assessments/backfill?limit=` → **200** with
     `candidate_count`, `persisted_count`, and `skipped_count` present (zeros OK;
     fail-closed skips / already-exists do not fail the gate)
   - SSH `alembic current` includes **`0009`** or `head`

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- New assessment math or methods
- Default-on calibration
- ACME / public DNS
- Actionable promotion, recommendations, orders

## Related documents

- [0046-phase-45-assessment-backfill.md](0046-phase-45-assessment-backfill.md)
- [0045-phase-44-nas-live-verify-phase-43.md](0045-phase-44-nas-live-verify-phase-43.md)
- [0041-phase-40-nas-lab-tls-cutover.md](0041-phase-40-nas-lab-tls-cutover.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
