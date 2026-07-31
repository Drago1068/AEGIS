# ADR-0139: Phase 138 NAS Live Verification of Phase 137

- Status: Accepted (live verified 2026-07-30; frontend recreate of ``811730c``)
- Date: 2026-07-30

## Context

Phase 137 extracts the latest-assessment detail panel section (ADR-0138). Operators need a
verified frontend redeploy on the UGREEN NAS under lab TLS after that lands
(behavior-preserving).

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 137 accepted via unit tests; live verify does not automate browser clicks.
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-30 for ``811730c``
(checklist item 64).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0138-phase-137-extract-latest-assessment-section.md](0138-phase-137-extract-latest-assessment-section.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
