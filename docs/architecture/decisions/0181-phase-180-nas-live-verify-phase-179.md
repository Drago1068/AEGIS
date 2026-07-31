# ADR-0181: Phase 180 NAS Live Verification of Phase 179

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``dd3aaa5``)
- Date: 2026-07-31

## Context

Phase 179 adds ``latest_calibration_horizon_key`` on evidence summary (ADR-0180). Operators
need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_calibration_horizon_key`` (null OK;
   checklist item 85).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``dd3aaa5``
(checklist item 85; AAPL ``latest_calibration_horizon_key=forward_return_5``;
``latest_calibration_id=66``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0180-phase-179-evidence-summary-latest-calibration-horizon-key.md](0180-phase-179-evidence-summary-latest-calibration-horizon-key.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
