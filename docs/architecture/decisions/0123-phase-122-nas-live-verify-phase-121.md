# ADR-0123: Phase 122 NAS Live Verification of Phase 121

- Status: Accepted (live verified 2026-07-30; frontend recreate of ``b0cf94d``)
- Date: 2026-07-30

## Context

Phase 121 names the outcome-label backfill control with its post-backfill refresh target
(ADR-0122). Operators need a verified frontend redeploy on the UGREEN NAS under lab TLS
after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 121 UX accepted via unit tests; live verify does not automate browser clicks.
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

- [0122-phase-121-outcome-label-backfill-names-refresh-target.md](0122-phase-121-outcome-label-backfill-names-refresh-target.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
