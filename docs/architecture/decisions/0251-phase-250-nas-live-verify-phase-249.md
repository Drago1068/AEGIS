# ADR-0251: Phase 250 NAS Live Verification of Phase 249

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 249 adds ``latest_assessment_last_available_label_bar_date`` (ADR-0250). Operators need
a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass.
3. Evidence-summary includes ``latest_assessment_last_available_label_bar_date`` (null OK;
   checklist item 120).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Live evidence (2026-07-31)

- Revision ``8c35d1d``; TLS recreate backend+frontend; verify passed.
- AAPL: ``latest_assessment_last_available_label_bar_date=2026-07-29`` (equals as_of;
  no forward closes yet);
  ``latest_assessment_forward_bar_shortfall=20``;
  ``latest_assessment_required_label_end_date=2026-08-26``;
  ``latest_assessment_label_block_reason=insufficient_forward_bars``.

## Related documents

- [0250-phase-249-evidence-summary-latest-last-available-label-bar-date.md](0250-phase-249-evidence-summary-latest-last-available-label-bar-date.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
