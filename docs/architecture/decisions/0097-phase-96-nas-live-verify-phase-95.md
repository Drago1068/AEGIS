# ADR-0097: Phase 96 NAS Live Verification of Phase 95

- Status: Accepted (live verified 2026-07-30; frontend recreate of ``2503fee``)
- Date: 2026-07-30

## Context

Phase 95 will refresh outcome-label history for the loaded assessment after backfill
(ADR-0096). Operators need a verified frontend redeploy on the UGREEN NAS under lab TLS
after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 95 UX accepted via unit tests; live verify does not automate browser clicks.
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 95 is on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0096-phase-95-outcome-label-backfill-refresh-loaded-assessment.md](0096-phase-95-outcome-label-backfill-refresh-loaded-assessment.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
