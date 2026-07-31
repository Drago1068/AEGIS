# ADR-0223: Phase 222 NAS Live Verification of Phase 221

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``8a3f9a7``)
- Date: 2026-07-31

## Context

Phase 221 adds ``most_recent_labeled_outcome_label_state`` on evidence summary (ADR-0222).
Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after
that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``most_recent_labeled_outcome_label_state``
   (null OK when no scan-labeled rows; checklist item 106).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``8a3f9a7``
(checklist item 106; AAPL ``most_recent_labeled_outcome_label_state=research_only`` with
``most_recent_labeled_outcome_label_id=82`` and ``schema_version=1``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0222-phase-221-evidence-summary-most-recent-labeled-outcome-label-state.md](0222-phase-221-evidence-summary-most-recent-labeled-outcome-label-state.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
