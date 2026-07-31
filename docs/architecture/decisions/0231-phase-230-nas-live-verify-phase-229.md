# ADR-0231: Phase 230 NAS Live Verification of Phase 229

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``9154394``)
- Date: 2026-07-31

## Context

Phase 229 adds ``scan_labeled_freshness_lag_trading_days`` on evidence summary
(ADR-0230). Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab
TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``scan_labeled_freshness_lag_trading_days``
   (null OK when either as_of date missing; checklist item 110).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``9154394``
(checklist item 110; AAPL ``scan_labeled_freshness_lag_trading_days=119`` with
``latest_as_of_trading_date=2026-07-29``,
``most_recent_labeled_outcome_label_as_of_trading_date=2026-02-05``,
``most_recent_labeled_outcome_label_id=82``).

### 3. Out of scope

New math beyond the lag diagnostic, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0230-phase-229-evidence-summary-scan-labeled-freshness-lag.md](0230-phase-229-evidence-summary-scan-labeled-freshness-lag.md)
- [0232-phase-231-evidence-summary-latest-assessment-is-label-ready.md](0232-phase-231-evidence-summary-latest-assessment-is-label-ready.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
