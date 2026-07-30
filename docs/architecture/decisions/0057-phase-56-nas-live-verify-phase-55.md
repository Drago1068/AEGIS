# ADR-0057: Phase 56 NAS Live Verification of Phase 55

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 55 defaults ``AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL`` to ``true`` and loads
research bars by distinct trading-date session depth (ADR-0056) so deep secondary (Polygon)
history can fill older assessment as-of dates when primary compact lookback is shallow.
Operators need a verified redeploy on the UGREEN NAS under the lab TLS profile.

## Decisions

### 1. Scope

Phase 56 is an **ops evidence gate** on the HTTPS lab profile:

1. Deploy current revision with the TLS overlay (native `linux/arm64` acceptable).
2. Ensure gitignored ``.env.nas`` sets:
   - ``AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL=true``
   - ``AEGIS_DAILY_BAR_OUTPUT_SIZE=full``
   - ``AEGIS_RESEARCH_BAR_LOAD_LIMIT=252`` (or higher within bounds)
   - secondary source + Polygon key configured (research path when AV rejects ``full``)
3. Recreate the backend so Compose injects the fill flag and session-depth code is live.
4. Authenticated assessment backfill for the verify symbol; prefer
   ``persisted_count >= 1`` when older secondary-filled as-of dates become assessable.
   Zeros OK only on re-verify when the limit window is already fully persisted.
5. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
6. Additionally confirm:
   - SSH `.env.nas` includes ``AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL=true``
   - Phase 48/50 coupling retained at outcome-label ``limit=20``
   - SSH `alembic current` includes **`0009`** or `head`

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- New assessment or label math beyond Phase 55
- Default-on calibration
- ACME / public DNS
- Actionable promotion, recommendations, orders

## Related documents

- [0056-phase-55-research-cross-source-session-depth.md](0056-phase-55-research-cross-source-session-depth.md)
- [0055-phase-54-nas-live-verify-phase-53.md](0055-phase-54-nas-live-verify-phase-53.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
