# ADR-0247: Phase 246 NAS Live Verification of Phase 245

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 245 adds ``latest_assessment_forward_bar_shortfall`` (ADR-0246). Operators need
a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass.
3. Evidence-summary includes ``latest_assessment_forward_bar_shortfall`` (null/0 OK;
   checklist item 118).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Live evidence (2026-07-31)

- Revision ``cbe7032``; TLS recreate backend+frontend; verify passed.
- AAPL: ``latest_assessment_forward_bar_shortfall=20``;
  ``latest_assessment_label_block_reason=insufficient_forward_bars``;
  ``latest_assessment_is_label_ready=False``;
  ``most_recent_unlabeled_assessment_id=126``;
  ``most_recent_unlabeled_as_of_trading_date=2026-07-29``;
  ``scan_unlabeled_label_ready_count=0``.

## Related documents

- [0246-phase-245-evidence-summary-latest-forward-bar-shortfall.md](0246-phase-245-evidence-summary-latest-forward-bar-shortfall.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
