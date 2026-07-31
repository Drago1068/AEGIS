# ADR-0179: Phase 178 NAS Live Verification of Phase 177

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``025958d``)
- Date: 2026-07-31

## Context

Phase 177 adds ``latest_calibration_id`` on evidence summary (ADR-0178). Operators need a
verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_calibration_id`` (null OK;
   checklist item 84).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``025958d``
(checklist item 84; AAPL ``latest_calibration_id=65``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0178-phase-177-evidence-summary-latest-calibration-id.md](0178-phase-177-evidence-summary-latest-calibration-id.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
