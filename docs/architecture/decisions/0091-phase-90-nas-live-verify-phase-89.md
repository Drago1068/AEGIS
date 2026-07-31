# ADR-0091: Phase 90 NAS Live Verification of Phase 89

- Status: Accepted (pending live evidence)
- Date: 2026-07-30

## Context

Phase 89 surfaces the download target assessment id on the outcome-label export control
(ADR-0090). Operators need a verified frontend redeploy on the UGREEN NAS under lab TLS.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 89 UX accepted via unit tests; live verify does not automate browser clicks.
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

- [0090-phase-89-outcome-label-download-names-assessment.md](0090-phase-89-outcome-label-download-names-assessment.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
