# ADR-0301: Phase 300 NAS Live Verification of Phase 299

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 299 added a research-index history chart from the assessments list
(ADR-0300). Operators needed a verified frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``ae48dd0`` via ``git archive``; preserved ``.env.nas``;
   rebuilt frontend TLS; waited ``/ready`` via docker-exec urllib.
2. ``verify.ps1`` passed. Live AAPL: ``list_count=20`` ``chartable_points=2``
   (deduped as_of; UI unit-tested). Sparse points motivate raising history limit next.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0300-phase-299-research-index-history-chart.md](0300-phase-299-research-index-history-chart.md)
- [0302-phase-301-assessment-history-limit-100.md](0302-phase-301-assessment-history-limit-100.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
