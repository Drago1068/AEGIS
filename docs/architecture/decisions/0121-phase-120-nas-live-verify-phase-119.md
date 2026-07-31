# ADR-0121: Phase 120 NAS Live Verification of Phase 119

- Status: Accepted (pending Phase 119 + live evidence)
- Date: 2026-07-30

## Context

Phase 119 makes calibration action chips/aria name ``latest`` explicitly (ADR-0120).
Operators need a verified frontend redeploy on the UGREEN NAS under lab TLS after that
lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 119 UX accepted via unit tests; live verify does not automate browser clicks.
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 119 is on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0120-phase-119-calibration-action-chips-name-latest.md](0120-phase-119-calibration-action-chips-name-latest.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
