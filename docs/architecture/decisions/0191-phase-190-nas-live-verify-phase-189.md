# ADR-0191: Phase 190 NAS Live Verification of Phase 189

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``346fcca``)
- Date: 2026-07-31

## Context

Phase 189 adds ``latest_calibration_method_version`` on evidence summary (ADR-0190). Operators
need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_calibration_method_version`` (null OK;
   checklist item 90).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``346fcca``
(checklist item 90; AAPL ``latest_calibration_method_version=2``;
``latest_calibration_method_id=research_calibration_v1``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0190-phase-189-evidence-summary-latest-calibration-method-version.md](0190-phase-189-evidence-summary-latest-calibration-method-version.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
