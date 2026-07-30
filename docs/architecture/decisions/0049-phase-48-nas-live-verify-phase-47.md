# ADR-0049: Phase 48 NAS Live Verification of Phase 47

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 47 changed assessment backfill to prefer label-ready as-of dates (ADR-0048) so Phase 43
labeling can persist. Operators need a verified redeploy of that revision on the UGREEN NAS
under the lab TLS profile, with evidence that newly persisted assessments can be labeled.

## Decisions

### 1. Scope

Phase 48 is an **ops evidence gate** on the HTTPS lab profile:

1. Deploy current revision with the TLS overlay (native `linux/arm64` acceptable).
2. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
3. Additionally confirm:
   - Unauthenticated `POST .../assessments/backfill` → **401** (unchanged)
   - Authenticated `POST .../assessments/backfill?limit=` → **200** with summary counts
   - Authenticated `POST .../outcome-labels/backfill?limit=` (verify uses ``limit=100`` so
     older label-ready rows beneath tip assessments are in scope) → **200** with summary
   - **Phase 48 coupling:** when assessment backfill reports ``persisted_count > 0``,
     the subsequent outcome-label backfill in the same verify run must report
     ``persisted_count >= 1`` (proves label-ready candidates). When assessment
     ``persisted_count == 0`` (already-exists / no candidates), label zeros remain OK.
   - SSH `alembic current` includes **`0009`** or `head`

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- New assessment or label math
- Default-on calibration
- ACME / public DNS
- Actionable promotion, recommendations, orders

## Related documents

- [0048-phase-47-label-ready-assessment-backfill.md](0048-phase-47-label-ready-assessment-backfill.md)
- [0047-phase-46-nas-live-verify-phase-45.md](0047-phase-46-nas-live-verify-phase-45.md)
- [0044-phase-43-outcome-label-backfill.md](0044-phase-43-outcome-label-backfill.md)
- [0041-phase-40-nas-lab-tls-cutover.md](0041-phase-40-nas-lab-tls-cutover.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
