# ADR-0059: Phase 58 NAS Live Verification of Phase 57

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 57 made outcome-label backfill readiness source-aware and raised scan/default limits
(ADR-0058). Operators need a verified redeploy on the UGREEN NAS under the lab TLS profile
so unlabeled label-ready assessments label without false-ready skip burn.

## Decisions

### 1. Scope

Phase 58 is an **ops evidence gate** on the HTTPS lab profile:

1. Deploy current revision with the TLS overlay (native `linux/arm64` acceptable).
2. Recreate the backend so Phase 57 selection + default ``limit=100`` are live.
3. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
4. Additionally confirm:
   - Authenticated ``POST .../outcome-labels/backfill?limit=100`` → **200**
   - Prefer ``persisted_count >= 1`` when ``assessment_count >= 1``; zeros OK when no
     unlabeled source-ready candidates remain in the scan window
   - Among selected candidates, prefer low ``skipped_count`` (source-aware selection);
     skips must remain fail-closed reasons only
   - Phase 48/50 coupling retained at outcome-label ``limit=20`` when assessments persist
   - SSH `alembic current` includes **`0009`** or `head`

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- New label math beyond Phase 57
- Default-on calibration
- ACME / public DNS
- Actionable promotion, recommendations, orders

## Related documents

- [0058-phase-57-source-aware-label-backfill-throughput.md](0058-phase-57-source-aware-label-backfill-throughput.md)
- [0057-phase-56-nas-live-verify-phase-55.md](0057-phase-56-nas-live-verify-phase-55.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
