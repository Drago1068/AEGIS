# ADR-0157: Phase 156 NAS Live Verification of Phase 155

- Status: Accepted (live verified 2026-07-30; backend+frontend recreate of ``cecb8b4``)
- Date: 2026-07-30

## Context

Phase 155 adds ``latest_input_source`` on evidence summary (ADR-0156). Operators need a
verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_input_source`` (null OK; checklist
   item 73).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-30 for ``cecb8b4``
(checklist item 73; AAPL ``latest_input_source=alpha_vantage``). Also hardened
``verify.ps1`` Alembic SSH capture (``2>&1``) so Alembic INFO logs do not abort
PowerShell ``Stop`` mid-gate.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0156-phase-155-evidence-summary-latest-input-source.md](0156-phase-155-evidence-summary-latest-input-source.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
