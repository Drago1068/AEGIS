# ADR-0117: Phase 116 NAS Live Verification of Phase 115

- Status: Accepted (pending Phase 115 + live evidence)
- Date: 2026-07-30

## Context

Phase 115 extracts outcome-label panel helpers into a dedicated module (ADR-0116).
Operators need a verified frontend redeploy on the UGREEN NAS under lab TLS after that
lands (behavior-preserving).

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 115 accepted via unit tests; live verify does not automate browser clicks.
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 115 is on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0116-phase-115-extract-outcome-label-panel-helpers.md](0116-phase-115-extract-outcome-label-panel-helpers.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
