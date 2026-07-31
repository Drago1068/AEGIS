# ADR-0161: Phase 160 NAS Live Verification of Phase 159

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``f78c02b``)
- Date: 2026-07-31

## Context

Phase 159 adds ``latest_method_version`` on evidence summary (ADR-0160). Operators need a
verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_method_version`` (null OK; checklist
   item 75).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``f78c02b``
(checklist item 75; AAPL ``latest_method_version=2``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0160-phase-159-evidence-summary-latest-method-version.md](0160-phase-159-evidence-summary-latest-method-version.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
