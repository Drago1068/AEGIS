# ADR-0255: Phase 254 NAS Live Verification of Phase 253

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 253 adds ``latest_assessment_min_horizon_required_label_end_date`` (ADR-0254).
Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after
that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass.
3. Evidence-summary includes ``latest_assessment_min_horizon_required_label_end_date``
   (null OK; checklist item 122).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Live evidence (2026-07-31)

- Revision ``c25e8b6``; TLS recreate backend+frontend; verify passed.
- AAPL: ``latest_assessment_min_horizon_required_label_end_date=2026-08-05`` (vs max
  ``latest_assessment_required_label_end_date=2026-08-26``);
  ``latest_assessment_min_horizon_forward_bar_shortfall=5``;
  ``latest_assessment_forward_bar_shortfall=20``;
  ``latest_assessment_last_available_label_bar_date=2026-07-29``;
  ``latest_as_of_trading_date=2026-07-29``;
  ``latest_assessment_label_block_reason=insufficient_forward_bars``.

## Related documents

- [0254-phase-253-evidence-summary-min-horizon-required-label-end-date.md](0254-phase-253-evidence-summary-min-horizon-required-label-end-date.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
