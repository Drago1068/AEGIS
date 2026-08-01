# ADR-0325: Phase 324 NAS Live Verification of Phase 323

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 323 elevated a full-horizon outcome-label CTA when tip is label-ready but
unlabeled (ADR-0324). Operators needed a verified NAS frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``6afff3f`` via ``git archive``; preserved ``.env.nas``; rebuilt
   frontend TLS; confirmed backend ``/ready``.
2. ``verify.ps1`` passed. Live AAPL still ``tip_ready=False`` ``forward_shortfall=20``
   (``required_end=2026-08-28``); ``tip_outcome_label_id=null``; CTA elevates when
   tip_ready+unlabeled (unit-tested).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0324-phase-323-full-horizon-unlock-cta.md](0324-phase-323-full-horizon-unlock-cta.md)
- [0326-phase-325-mixed-unlabeled-backlog-cta.md](0326-phase-325-mixed-unlabeled-backlog-cta.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
