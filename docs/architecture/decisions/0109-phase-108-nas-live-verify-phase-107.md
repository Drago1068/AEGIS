# ADR-0109: Phase 108 NAS Live Verification of Phase 107

- Status: Accepted (pending Phase 107 + live evidence)
- Date: 2026-07-30

## Context

Phase 107 renames the shared active outcome-label assessment id helper (ADR-0108).
Operators need a verified frontend redeploy on the UGREEN NAS under lab TLS after that
lands (behavior-preserving).

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 107 accepted via unit tests; live verify does not automate browser clicks.
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 107 is on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0108-phase-107-rename-active-outcome-label-assessment-id.md](0108-phase-107-rename-active-outcome-label-assessment-id.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
