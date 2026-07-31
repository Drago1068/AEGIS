# ADR-0125: Phase 124 NAS Live Verification of Phase 123

- Status: Accepted (live verified 2026-07-30; frontend recreate of ``5afa71e``)
- Date: 2026-07-30

## Context

Phase 123 extracts the research assessment action toolbar component (ADR-0124). Operators
need a verified frontend redeploy on the UGREEN NAS under lab TLS after that lands
(behavior-preserving).

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 123 accepted via unit tests; live verify does not automate browser clicks.
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

- [0124-phase-123-extract-research-assessment-action-toolbar.md](0124-phase-123-extract-research-assessment-action-toolbar.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
