# ADR-0227: Phase 226 NAS Live Verification of Phase 225

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``1a4091f``)
- Date: 2026-07-31

## Context

Phase 225 adds ``most_recent_labeled_outcome_label_computed_at`` on evidence summary
(ADR-0226). Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab
TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``most_recent_labeled_outcome_label_computed_at``
   (null OK when no scan-labeled rows; checklist item 108).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``1a4091f``
(checklist item 108; AAPL
``most_recent_labeled_outcome_label_computed_at=2026-07-30T21:25:15.962739Z`` with
``most_recent_labeled_outcome_label_id=82`` and ``bar_source=polygon``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0226-phase-225-evidence-summary-most-recent-labeled-outcome-label-computed-at.md](0226-phase-225-evidence-summary-most-recent-labeled-outcome-label-computed-at.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
