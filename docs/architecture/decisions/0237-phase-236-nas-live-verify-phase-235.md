# ADR-0237: Phase 236 NAS Live Verification of Phase 235

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``821aed1``)
- Date: 2026-07-31

## Context

Phase 235 adds ``most_recent_labelable_as_of_trading_date`` (ADR-0236). Operators need a
verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass (prior gates remain).
3. Evidence-summary includes ``most_recent_labelable_as_of_trading_date`` (null OK; checklist
   item 113).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout. Live verify passed 2026-07-31 for ``821aed1`` (checklist item 113;
AAPL ``most_recent_labelable_as_of_trading_date=2026-02-05`` with
``most_recent_labeled_outcome_label_as_of_trading_date=2026-02-05``,
``latest_assessment_label_block_reason=insufficient_forward_bars``).

### 3. Out of scope

New scoring math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0236-phase-235-evidence-summary-most-recent-labelable-as-of-trading-date.md](0236-phase-235-evidence-summary-most-recent-labelable-as-of-trading-date.md)
- [0238-phase-237-evidence-summary-most-recent-unlabeled-labelable-as-of.md](0238-phase-237-evidence-summary-most-recent-unlabeled-labelable-as-of.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
