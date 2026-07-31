# ADR-0233: Phase 232 NAS Live Verification of Phase 231

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``d594387``)
- Date: 2026-07-31

## Context

Phase 231 adds ``latest_assessment_is_label_ready`` on evidence summary (ADR-0232). Operators
need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_assessment_is_label_ready``
   (null OK when no latest assessment; checklist item 111).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``d594387``
(checklist item 111; AAPL ``latest_assessment_is_label_ready=False`` with
``latest_assessment_id=126``, ``latest_outcome_label_id=null``,
``scan_labeled_freshness_lag_trading_days=119``).

### 3. Out of scope

New scoring math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0232-phase-231-evidence-summary-latest-assessment-is-label-ready.md](0232-phase-231-evidence-summary-latest-assessment-is-label-ready.md)
- [0234-phase-233-evidence-summary-latest-assessment-label-block-reason.md](0234-phase-233-evidence-summary-latest-assessment-label-block-reason.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
