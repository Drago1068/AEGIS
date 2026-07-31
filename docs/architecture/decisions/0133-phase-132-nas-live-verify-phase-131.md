# ADR-0133: Phase 132 NAS Live Verification of Phase 131

- Status: Accepted (pending Phase 131 + live evidence)
- Date: 2026-07-30

## Context

Phase 131 extracts the calibration readiness panel section (ADR-0132). Operators need a
verified frontend redeploy on the UGREEN NAS under lab TLS after that lands
(behavior-preserving).

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 131 accepted via unit tests; live verify does not automate browser clicks.
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 131 is on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0132-phase-131-extract-calibration-readiness-section.md](0132-phase-131-extract-calibration-readiness-section.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
