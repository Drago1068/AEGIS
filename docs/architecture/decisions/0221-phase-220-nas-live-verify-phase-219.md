# ADR-0221: Phase 220 NAS Live Verification of Phase 219

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``a2b36b8``)
- Date: 2026-07-31

## Context

Phase 219 adds ``most_recent_labeled_outcome_label_schema_version`` on evidence summary
(ADR-0220). Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab
TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``most_recent_labeled_outcome_label_schema_version``
   (null OK when no scan-labeled rows; checklist item 105).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``a2b36b8``
(checklist item 105; AAPL ``most_recent_labeled_outcome_label_schema_version=1`` with
``most_recent_labeled_outcome_label_id=82``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0220-phase-219-evidence-summary-most-recent-labeled-outcome-label-schema-version.md](0220-phase-219-evidence-summary-most-recent-labeled-outcome-label-schema-version.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
