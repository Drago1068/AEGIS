# ADR-0067: Phase 66 NAS Live Verification of Phase 65

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 65 prefers mixed unlabeled label-ready assessments in outcome-label backfill and
resolves true-mixed label bar sources from as-of provenance (ADR-0066). Operators need a
verified redeploy on the UGREEN NAS under the lab TLS profile.

## Decisions

### 1. Scope

Phase 66 is an **ops evidence gate** on the HTTPS lab profile:

1. Deploy current revision with the TLS overlay (native `linux/arm64` acceptable).
2. Recreate the **backend** so Phase 65 selection + mixed bar-source resolution are live.
3. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
4. Additionally confirm authenticated ``POST .../outcome-labels/backfill?limit=100`` → **200**
   (Phase 58 path). Prefer ``assessment_count >= 1`` / ``persisted_count >= 1`` when unlabeled
   mixed-ready candidates exist; zeros OK when the scan window has no remaining unlabeled
   label-ready rows.
5. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- New label math beyond Phase 65
- Default-on calibration
- ACME / public DNS
- Actionable promotion, recommendations, orders

## Related documents

- [0066-phase-65-prefer-mixed-label-backfill.md](0066-phase-65-prefer-mixed-label-backfill.md)
- [0059-phase-58-nas-live-verify-phase-57.md](0059-phase-58-nas-live-verify-phase-57.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
