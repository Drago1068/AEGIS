# ADR-0045: Phase 44 NAS Live Verification of Phase 43

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 43 added research-only historical outcome-label backfill
(`POST /research/{symbol}/outcome-labels/backfill`). Operators need a verified redeploy of
that revision on the UGREEN NAS under the lab TLS profile without expanding product
capabilities.

## Decisions

### 1. Scope

Phase 44 is an **ops evidence gate** on the HTTPS lab profile:

1. Deploy current revision with the TLS overlay (native `linux/arm64` acceptable).
2. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
3. Additionally confirm:
   - Unauthenticated `POST .../outcome-labels/backfill` → **401**
   - Authenticated `POST .../outcome-labels/backfill?limit=` → **200** with
     `assessment_count`, `persisted_count`, and `skipped_count` present (zeros OK;
     fail-closed skips do not fail the gate)
   - SSH `alembic current` includes **`0009`** or `head`

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- New labeling math or horizons
- Default-on calibration
- ACME / public DNS
- Actionable promotion, recommendations, orders

## Related documents

- [0044-phase-43-outcome-label-backfill.md](0044-phase-43-outcome-label-backfill.md)
- [0043-phase-42-nas-live-verify-phase-41.md](0043-phase-42-nas-live-verify-phase-41.md)
- [0041-phase-40-nas-lab-tls-cutover.md](0041-phase-40-nas-lab-tls-cutover.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
