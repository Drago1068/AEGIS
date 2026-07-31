# ADR-0101: Phase 100 NAS Live Verification of Phase 99

- Status: Accepted (live verified 2026-07-30; frontend recreate of ``545c13e``)
- Date: 2026-07-30

## Context

Phase 99 will name the calibrations download target as ``latest`` assessment id
(ADR-0100). Operators need a verified frontend redeploy on the UGREEN NAS under lab TLS
after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 99 UX accepted via unit tests; live verify does not automate browser clicks.
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 99 is on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0100-phase-99-calibrations-download-names-latest.md](0100-phase-99-calibrations-download-names-latest.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
