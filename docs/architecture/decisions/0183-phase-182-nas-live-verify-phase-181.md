# ADR-0183: Phase 182 NAS Live Verification of Phase 181

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``b08c4ce``)
- Date: 2026-07-31

## Context

Phase 181 adds ``latest_calibration_computed_at`` on evidence summary (ADR-0182). Operators
need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_calibration_computed_at`` (null OK;
   checklist item 86).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``b08c4ce``
(checklist item 86; AAPL ``latest_calibration_computed_at=2026-07-31T05:25:31.947262Z``;
``latest_calibration_id=67``; ``latest_calibration_horizon_key=forward_return_5``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0182-phase-181-evidence-summary-latest-calibration-computed-at.md](0182-phase-181-evidence-summary-latest-calibration-computed-at.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
