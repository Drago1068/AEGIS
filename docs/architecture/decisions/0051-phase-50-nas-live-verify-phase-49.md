# ADR-0051: Phase 50 NAS Live Verification of Phase 49

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 49 changed outcome-label backfill to prefer unlabeled, label-ready assessments
(ADR-0050) so default ``limit=20`` can grow the labeled corpus without tip / already-labeled
waste. Operators need a verified redeploy of that revision on the UGREEN NAS under the lab
TLS profile.

## Decisions

### 1. Scope

Phase 50 is an **ops evidence gate** on the HTTPS lab profile:

1. Deploy current revision with the TLS overlay (native `linux/arm64` acceptable).
2. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
3. Additionally confirm:
   - Unauthenticated `POST .../outcome-labels/backfill` → **401** (unchanged)
   - Authenticated `POST .../outcome-labels/backfill?limit=20` → **200** with summary counts
   - **Phase 48 coupling retained:** when assessment backfill ``persisted_count > 0``,
     outcome-label backfill in the same run must ``persisted_count >= 1`` at ``limit=20``
     (proves Phase 49 selection reaches label-ready rows without ``limit=100``)
   - When assessment ``persisted_count == 0``, label zeros remain OK
   - SSH `alembic current` includes **`0009`** or `head`

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- New assessment or label math
- Default-on calibration
- ACME / public DNS
- Actionable promotion, recommendations, orders

## Related documents

- [0050-phase-49-prefer-unlabeled-label-backfill.md](0050-phase-49-prefer-unlabeled-label-backfill.md)
- [0049-phase-48-nas-live-verify-phase-47.md](0049-phase-48-nas-live-verify-phase-47.md)
- [0041-phase-40-nas-lab-tls-cutover.md](0041-phase-40-nas-lab-tls-cutover.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
