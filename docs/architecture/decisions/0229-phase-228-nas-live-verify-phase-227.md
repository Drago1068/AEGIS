# ADR-0229: Phase 228 NAS Live Verification of Phase 227

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``285dafe``)
- Date: 2026-07-31

## Context

Phase 227 adds ``most_recent_labeled_outcome_label_as_of_trading_date`` on evidence summary
(ADR-0228). Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab
TLS after that lands. This closes the planned scan-labeled scalar provenance series
(Phases 213–228).

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes
   ``most_recent_labeled_outcome_label_as_of_trading_date`` (null OK when no scan-labeled
   rows; checklist item 109).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``285dafe``
(checklist item 109; AAPL
``most_recent_labeled_outcome_label_as_of_trading_date=2026-02-05`` with
``most_recent_labeled_outcome_label_id=82`` and
``computed_at=2026-07-30T21:25:15.962739Z``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0228-phase-227-evidence-summary-most-recent-labeled-outcome-label-as-of-trading-date.md](0228-phase-227-evidence-summary-most-recent-labeled-outcome-label-as-of-trading-date.md)
- [0230-phase-229-evidence-summary-scan-labeled-freshness-lag.md](0230-phase-229-evidence-summary-scan-labeled-freshness-lag.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
