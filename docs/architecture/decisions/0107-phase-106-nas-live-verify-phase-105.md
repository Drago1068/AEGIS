# ADR-0107: Phase 106 NAS Live Verification of Phase 105

- Status: Accepted (pending live evidence)
- Date: 2026-07-30

## Context

Phase 105 adds one-click load of outcome labels for ``latest`` when the panel is on another
assessment (ADR-0106). Operators need a verified frontend redeploy on the UGREEN NAS under
lab TLS.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 105 UX accepted via unit tests; live verify does not automate browser clicks.
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

- [0106-phase-105-load-labels-for-latest.md](0106-phase-105-load-labels-for-latest.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
