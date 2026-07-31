# ADR-0171: Phase 170 NAS Live Verification of Phase 169

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``fcf4123``)
- Date: 2026-07-31

## Context

Phase 169 adds ``latest_event_time`` on evidence summary (ADR-0170). Operators need a
verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_event_time`` (null OK;
   checklist item 80).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``fcf4123``
(checklist item 80; AAPL ``latest_event_time=2026-07-29T23:59:59Z``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0170-phase-169-evidence-summary-latest-event-time.md](0170-phase-169-evidence-summary-latest-event-time.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
