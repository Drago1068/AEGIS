# ADR-0225: Phase 224 NAS Live Verification of Phase 223

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``7d73b42``)
- Date: 2026-07-31

## Context

Phase 223 adds ``most_recent_labeled_outcome_label_bar_source`` on evidence summary (ADR-0224).
Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after
that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``most_recent_labeled_outcome_label_bar_source``
   (null OK when no scan-labeled rows; checklist item 107).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``7d73b42``
(checklist item 107; AAPL ``most_recent_labeled_outcome_label_bar_source=polygon`` with
``most_recent_labeled_outcome_label_id=82``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0224-phase-223-evidence-summary-most-recent-labeled-outcome-label-bar-source.md](0224-phase-223-evidence-summary-most-recent-labeled-outcome-label-bar-source.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
