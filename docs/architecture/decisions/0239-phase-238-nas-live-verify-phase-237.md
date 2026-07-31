# ADR-0239: Phase 238 NAS Live Verification of Phase 237

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 237 adds ``most_recent_unlabeled_labelable_as_of_trading_date`` (ADR-0238).
Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after
that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass.
3. Evidence-summary includes ``most_recent_unlabeled_labelable_as_of_trading_date`` (null OK;
   checklist item 114).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Live evidence (2026-07-31)

- Revision ``c76b75c``; TLS recreate backend+frontend; verify passed.
- AAPL: ``most_recent_labelable_as_of_trading_date=2026-02-05``;
  ``most_recent_unlabeled_labelable_as_of_trading_date=null``;
  ``unlabeled_assessment_count=3``; ``latest_assessment_label_block_reason=insufficient_forward_bars``.
- Interpretation: newest labelable row is already labeled; remaining unlabeled rows are not
  label-ready (backfill next-target empty until forward bars exist).

## Related documents

- [0238-phase-237-evidence-summary-most-recent-unlabeled-labelable-as-of.md](0238-phase-237-evidence-summary-most-recent-unlabeled-labelable-as-of.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
