# ADR-0055: Phase 54 NAS Live Verification of Phase 53

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 53 defaulted ``AEGIS_DAILY_BAR_OUTPUT_SIZE`` to ``full`` and wired it through Compose
(ADR-0054) so ``AEGIS_RESEARCH_BAR_LOAD_LIMIT=252`` can load deeper stored series after
re-ingest. Operators need a verified redeploy on the UGREEN NAS under the lab TLS profile
with ``full`` lookback applied and ingest re-run.

## Decisions

### 1. Scope

Phase 54 is an **ops evidence gate** on the HTTPS lab profile:

1. Deploy current revision with the TLS overlay (native `linux/arm64` acceptable).
2. Ensure gitignored ``.env.nas`` sets:
   - ``AEGIS_DAILY_BAR_OUTPUT_SIZE=full``
   - ``AEGIS_RESEARCH_BAR_LOAD_LIMIT=252`` (or higher within bounds)
3. Recreate the backend so Compose injects both settings.
4. Authenticated on-demand ingest for the verify symbol (and optionally other watchlist
   symbols) so append-only storage can grow beyond compact (~100) bars.
5. Ensure Compose injects daily-bar primary/secondary source and Polygon API key into the
   backend (free Alpha Vantage rejects ``outputsize=full``; secondary Polygon is the
   research path for deep history).
6. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
7. Additionally confirm:
   - SSH `.env.nas` includes ``AEGIS_DAILY_BAR_OUTPUT_SIZE=full``
   - Prefer assessment backfill ``persisted_count >= 1`` when deeper bars unlock new
     label-ready as-of dates; zeros OK only when candidates already exist in the limit
     window (re-verify) or providers return no new older bars
   - Phase 48/50 coupling retained at outcome-label ``limit=20``
   - SSH `alembic current` includes **`0009`** or `head`

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- New assessment or label math
- Default-on calibration
- ACME / public DNS
- Actionable promotion, recommendations, orders

## Related documents

- [0054-phase-53-full-daily-bar-history.md](0054-phase-53-full-daily-bar-history.md)
- [0053-phase-52-nas-live-verify-phase-51.md](0053-phase-52-nas-live-verify-phase-51.md)
- [0052-phase-51-research-bar-load-limit.md](0052-phase-51-research-bar-load-limit.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
