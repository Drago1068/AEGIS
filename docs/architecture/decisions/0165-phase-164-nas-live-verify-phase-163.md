# ADR-0165: Phase 164 NAS Live Verification of Phase 163

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``d120c76``)
- Date: 2026-07-31

## Context

Phase 163 adds ``latest_lookback_start_date`` on evidence summary (ADR-0164). Operators need
a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_lookback_start_date`` (null OK;
   checklist item 77).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``d120c76``
(checklist item 77; AAPL ``latest_lookback_start_date=2026-07-01``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0164-phase-163-evidence-summary-latest-lookback-start.md](0164-phase-163-evidence-summary-latest-lookback-start.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
