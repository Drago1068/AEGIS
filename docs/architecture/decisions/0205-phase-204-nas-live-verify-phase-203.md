# ADR-0205: Phase 204 NAS Live Verification of Phase 203

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``32b2040``)
- Date: 2026-07-31

## Context

Phase 203 adds ``latest_outcome_label_method_version`` on evidence summary (ADR-0204).
Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after
that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_outcome_label_method_version`` (null OK;
   checklist item 97).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``32b2040``
(checklist item 97; AAPL ``latest_outcome_label_method_version=null`` — latest assessment
unlabeled; ``latest_outcome_label_id=null``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0204-phase-203-evidence-summary-latest-outcome-label-method-version.md](0204-phase-203-evidence-summary-latest-outcome-label-method-version.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
