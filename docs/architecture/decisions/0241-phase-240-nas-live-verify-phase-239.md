# ADR-0241: Phase 240 NAS Live Verification of Phase 239

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 239 adds ``scan_unlabeled_label_ready_count`` (ADR-0240). Operators need a verified
backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass.
3. Evidence-summary includes ``scan_unlabeled_label_ready_count`` (0 OK; checklist item 115).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Live evidence (2026-07-31)

- Revision ``b9e5033``; TLS recreate backend+frontend; verify passed.
- AAPL: ``scan_unlabeled_label_ready_count=0``;
  ``most_recent_unlabeled_labelable_as_of_trading_date=null``;
  ``unlabeled_assessment_count=3``;
  ``latest_assessment_label_block_reason=insufficient_forward_bars``.
- Interpretation: zero ready backfill candidates; the three unlabeled rows are not
  label-ready (matches empty outcome-label backfill).

## Related documents

- [0240-phase-239-evidence-summary-scan-unlabeled-label-ready-count.md](0240-phase-239-evidence-summary-scan-unlabeled-label-ready-count.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
