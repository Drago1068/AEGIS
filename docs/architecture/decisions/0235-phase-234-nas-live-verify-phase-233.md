# ADR-0235: Phase 234 NAS Live Verification of Phase 233

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``bc554c7``)
- Date: 2026-07-31

## Context

Phase 233 adds ``latest_assessment_label_block_reason`` on evidence summary (ADR-0234).
Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after
that lands. Earlier blocked by NAS SSH port 22 refusal; SSH restored 2026-07-31.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_assessment_label_block_reason``
   (null OK when ready or no assessment; checklist item 112).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``bc554c7``
(checklist item 112; AAPL ``latest_assessment_label_block_reason=insufficient_forward_bars``
with ``latest_assessment_is_label_ready=False``, ``latest_assessment_id=126``,
``scan_labeled_freshness_lag_trading_days=119``).

### 3. Out of scope

New scoring math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0234-phase-233-evidence-summary-latest-assessment-label-block-reason.md](0234-phase-233-evidence-summary-latest-assessment-label-block-reason.md)
- [0236-phase-235-evidence-summary-most-recent-labelable-as-of-trading-date.md](0236-phase-235-evidence-summary-most-recent-labelable-as-of-trading-date.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
