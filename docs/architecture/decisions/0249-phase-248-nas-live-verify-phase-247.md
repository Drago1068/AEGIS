# ADR-0249: Phase 248 NAS Live Verification of Phase 247

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 247 adds ``latest_assessment_required_label_end_date`` (ADR-0248). Operators need
a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass.
3. Evidence-summary includes ``latest_assessment_required_label_end_date`` (null OK;
   checklist item 119).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Live evidence (2026-07-31)

- Revision ``3fe7edf``; TLS recreate backend+frontend; verify passed.
- AAPL: ``latest_assessment_required_label_end_date=2026-08-26``;
  ``latest_assessment_forward_bar_shortfall=20``;
  ``latest_assessment_label_block_reason=insufficient_forward_bars``;
  ``latest_as_of_trading_date=2026-07-29``;
  ``scan_unlabeled_label_ready_count=0``.

## Related documents

- [0248-phase-247-evidence-summary-latest-required-label-end-date.md](0248-phase-247-evidence-summary-latest-required-label-end-date.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
