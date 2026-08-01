# ADR-0291: Phase 290 NAS Live Verification of Phase 289

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 289 grouped tip / freshness / unlabeled-empty labeling callouts under one
research-only region (ADR-0290). Operators needed a verified frontend redeploy under
lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``39ff608`` via ``git archive``; preserved ``.env.nas``; rebuilt
   frontend TLS compose.
2. ``verify.ps1`` passed (exit 0) against lab HTTPS with insecure + resolve.
3. Alembic ``0009`` / ``head``.

### 2. Live evidence (AAPL, 2026-07-31)

- Phase 290 triggers=``tip_not_ready,freshness_lag,unlabeled_empty``
- Tip shortfall ``20`` / required end ``2026-08-28``; lag ``121``; unlabeled ready ``0``
- Post-ingest note: ``primary_fetch_fallback=null`` (polygon tip) on this run
- Upload ≠ verified; retain verify stdout.

## Related documents

- [0290-phase-289-labeling-diagnostics-group.md](0290-phase-289-labeling-diagnostics-group.md)
- [0292-phase-291-mixed-unlabeled-backlog-callout.md](0292-phase-291-mixed-unlabeled-backlog-callout.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
