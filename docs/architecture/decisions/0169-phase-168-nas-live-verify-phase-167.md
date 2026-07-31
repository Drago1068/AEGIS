# ADR-0169: Phase 168 NAS Live Verification of Phase 167

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``4fecc07``)
- Date: 2026-07-31

## Context

Phase 167 adds ``latest_computed_at`` on evidence summary (ADR-0168). Operators need a
verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_computed_at`` (null OK;
   checklist item 79).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``4fecc07``
(checklist item 79; AAPL ``latest_computed_at=2026-07-30T22:00:01.230802Z``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0168-phase-167-evidence-summary-latest-computed-at.md](0168-phase-167-evidence-summary-latest-computed-at.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
