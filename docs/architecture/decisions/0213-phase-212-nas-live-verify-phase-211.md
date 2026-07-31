# ADR-0213: Phase 212 NAS Live Verification of Phase 211

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``d0f8bb8``)
- Date: 2026-07-31

## Context

Phase 211 adds ``latest_outcome_label_as_of_trading_date`` on evidence summary (ADR-0212).
Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after
that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_outcome_label_as_of_trading_date``
   (null OK; checklist item 101).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``d0f8bb8``
(checklist item 101; AAPL ``latest_outcome_label_as_of_trading_date=null`` — latest
assessment unlabeled; ``latest_outcome_label_id=null``). Declares the absolute-latest
``latest_outcome_label_*`` scalar provenance series complete.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0212-phase-211-evidence-summary-latest-outcome-label-as-of-trading-date.md](0212-phase-211-evidence-summary-latest-outcome-label-as-of-trading-date.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
