# ADR-0253: Phase 252 NAS Live Verification of Phase 251

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 251 adds ``latest_assessment_min_horizon_forward_bar_shortfall`` (ADR-0252). Operators
need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass.
3. Evidence-summary includes ``latest_assessment_min_horizon_forward_bar_shortfall``
   (null/0 OK; checklist item 121).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Live evidence (2026-07-31)

- Revision ``6858194``; TLS recreate backend+frontend; verify passed.
- AAPL: ``latest_assessment_min_horizon_forward_bar_shortfall=5`` (vs max shortfall ``20``);
  ``latest_assessment_last_available_label_bar_date=2026-07-29``;
  ``latest_assessment_required_label_end_date=2026-08-26``;
  ``latest_assessment_label_block_reason=insufficient_forward_bars``.

## Related documents

- [0252-phase-251-evidence-summary-min-horizon-forward-bar-shortfall.md](0252-phase-251-evidence-summary-min-horizon-forward-bar-shortfall.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
