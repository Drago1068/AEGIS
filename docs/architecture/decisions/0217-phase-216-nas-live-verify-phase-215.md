# ADR-0217: Phase 216 NAS Live Verification of Phase 215

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``058f0c5``)
- Date: 2026-07-31

## Context

Phase 215 adds ``most_recent_labeled_outcome_label_method_id`` on evidence summary (ADR-0216).
Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after
that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``most_recent_labeled_outcome_label_method_id``
   (null OK when no scan-labeled rows; checklist item 103).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``058f0c5``
(checklist item 103; AAPL ``most_recent_labeled_outcome_label_method_id=forward_total_return_v1``
with ``most_recent_labeled_outcome_label_id=82``; absolute-latest label scalars null).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0216-phase-215-evidence-summary-most-recent-labeled-outcome-label-method-id.md](0216-phase-215-evidence-summary-most-recent-labeled-outcome-label-method-id.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
