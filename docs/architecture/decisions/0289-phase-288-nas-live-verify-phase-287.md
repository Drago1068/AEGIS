# ADR-0289: Phase 288 NAS Live Verification of Phase 287

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 287 elevated an empty unlabeled label-ready callout from existing
evidence-summary fields (ADR-0288). Operators needed a verified frontend redeploy
under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``1c1ee45`` via ``git archive``; preserved ``.env.nas``; rebuilt
   frontend TLS compose.
2. ``verify.ps1`` passed (exit 0) against lab HTTPS with insecure + resolve.
3. Alembic ``0009`` / ``head``.

### 2. Live evidence (AAPL, 2026-07-31)

- ``scan_unlabeled_label_ready_count=0``
- ``most_recent_unlabeled_assessment_id=180``
- ``most_recent_unlabeled_as_of_trading_date=2026-07-31``
- Tip still ``label_ready=False`` / shortfall ``20``; freshness lag ``121``
- Upload ≠ verified; retain verify stdout.

## Related documents

- [0288-phase-287-unlabeled-label-ready-empty-callout.md](0288-phase-287-unlabeled-label-ready-empty-callout.md)
- [0290-phase-289-labeling-diagnostics-group.md](0290-phase-289-labeling-diagnostics-group.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
