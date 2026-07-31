# ADR-0103: Phase 102 NAS Live Verification of Phase 101

- Status: Accepted (live verified 2026-07-30; frontend recreate of ``9916ae2``)
- Date: 2026-07-30

## Context

Phase 101 names the compute-calibration control with ``latest`` assessment id (ADR-0102).
Operators need a verified frontend redeploy on the UGREEN NAS under lab TLS.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 101 UX accepted via unit tests; live verify does not automate browser clicks.
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0102-phase-101-compute-calibration-names-latest.md](0102-phase-101-compute-calibration-names-latest.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
