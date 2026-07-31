# ADR-0195: Phase 194 NAS Live Verification of Phase 193

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``c72ec84``)
- Date: 2026-07-31

## Context

Phase 193 adds ``latest_calibration_state`` on evidence summary (ADR-0194). Operators need a
verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_calibration_state`` (null OK;
   checklist item 92).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``c72ec84``
(checklist item 92; AAPL ``latest_calibration_state=research_only``;
``latest_calibration_schema_version=1``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0194-phase-193-evidence-summary-latest-calibration-state.md](0194-phase-193-evidence-summary-latest-calibration-state.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
