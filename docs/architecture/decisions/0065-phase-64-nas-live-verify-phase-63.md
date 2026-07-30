# ADR-0065: Phase 64 NAS Live Verification of Phase 63

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 63 added a console one-click control from evidence-summary
``mixed_component_source_assessment_count`` to assessment history ``component_source=mixed``
(ADR-0064). Operators need a verified redeploy on the UGREEN NAS under the lab TLS profile
so the frontend ships that control.

## Decisions

### 1. Scope

Phase 64 is an **ops evidence gate** on the HTTPS lab profile:

1. Deploy current revision with the TLS overlay (native `linux/arm64` acceptable).
2. Recreate **frontend** (backend optional; Phase 61 APIs already live from Phase 62).
3. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory),
   including Phase 62 ``component_source=mixed`` list+export (the API path the button uses).
4. Console one-click UX is accepted via Phase 63 unit tests; live verify does not automate
   browser clicks.
5. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- New assessment/label math
- Default-on calibration
- ACME / public DNS
- Actionable promotion, recommendations, orders

## Related documents

- [0064-phase-63-one-click-mixed-filter.md](0064-phase-63-one-click-mixed-filter.md)
- [0063-phase-62-nas-live-verify-phase-61.md](0063-phase-62-nas-live-verify-phase-61.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
