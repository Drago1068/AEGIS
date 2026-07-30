# ADR-0053: Phase 52 NAS Live Verification of Phase 51

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 51 added ``AEGIS_RESEARCH_BAR_LOAD_LIMIT`` (default 252) so assessment and
outcome-label paths can load deeper recent-bar history (ADR-0052). Operators need a
verified redeploy on the UGREEN NAS under the lab TLS profile with that setting applied.

## Decisions

### 1. Scope

Phase 52 is an **ops evidence gate** on the HTTPS lab profile:

1. Deploy current revision with the TLS overlay (native `linux/arm64` acceptable).
2. Ensure gitignored ``.env.nas`` sets ``AEGIS_RESEARCH_BAR_LOAD_LIMIT=252`` (or higher within
   bounds) on the NAS project directory before recreate. Compose backend environment must
   pass the variable through (``docker-compose.yml`` / NAS overlay).
3. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
4. Additionally confirm:
   - Authenticated `POST .../assessments/backfill?limit=20` → **200** with summary counts
   - Prefer ``persisted_count >= 1`` when stored bars unlock new label-ready as-of dates
     beyond the prior 120-bar window; zeros OK if the symbol is already saturated within
     the available stored series (ingest depth remains out of scope for this phase)
   - Phase 48/50 coupling retained for outcome-label backfill at ``limit=20``
   - SSH `alembic current` includes **`0009`** or `head`

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- Changing provider ``outputsize`` / forcing re-ingest
- New assessment or label math
- Default-on calibration
- ACME / public DNS
- Actionable promotion, recommendations, orders

## Related documents

- [0052-phase-51-research-bar-load-limit.md](0052-phase-51-research-bar-load-limit.md)
- [0051-phase-50-nas-live-verify-phase-49.md](0051-phase-50-nas-live-verify-phase-49.md)
- [0041-phase-40-nas-lab-tls-cutover.md](0041-phase-40-nas-lab-tls-cutover.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
