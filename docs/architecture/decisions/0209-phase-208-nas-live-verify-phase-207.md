# ADR-0209: Phase 208 NAS Live Verification of Phase 207

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``5f5d8f5``)
- Date: 2026-07-31

## Context

Phase 207 adds ``latest_outcome_label_state`` on evidence summary (ADR-0208). Operators need
a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_outcome_label_state`` (null OK;
   checklist item 99).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``5f5d8f5``
(checklist item 99; AAPL ``latest_outcome_label_state=null`` — latest assessment unlabeled;
``latest_outcome_label_id=null``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0208-phase-207-evidence-summary-latest-outcome-label-state.md](0208-phase-207-evidence-summary-latest-outcome-label-state.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
