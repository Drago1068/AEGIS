# ADR-0243: Phase 242 NAS Live Verification of Phase 241

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 241 adds ``most_recent_unlabeled_assessment_id`` (ADR-0242). Operators need a
verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass.
3. Evidence-summary includes ``most_recent_unlabeled_assessment_id`` (null OK;
   checklist item 116).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Live evidence (2026-07-31)

- Revision ``c7d5f7b``; TLS recreate backend+frontend; verify passed.
- AAPL: ``most_recent_unlabeled_assessment_id=126`` (equals ``latest_assessment_id``);
  ``scan_unlabeled_label_ready_count=0``;
  ``latest_assessment_label_block_reason=insufficient_forward_bars``.

## Related documents

- [0242-phase-241-evidence-summary-most-recent-unlabeled-assessment-id.md](0242-phase-241-evidence-summary-most-recent-unlabeled-assessment-id.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
