# ADR-0305: Phase 304 NAS Live Verification of Phase 303

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 303 added a coverage-confidence history chart from the assessments list
(ADR-0304), labeled distinct from probability confidence. Operators needed a
verified frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``704ed4e`` via ``git archive``; preserved ``.env.nas``;
   rebuilt frontend TLS; waited ``/ready`` via docker-exec urllib.
2. ``verify.ps1`` passed. Live AAPL: ``list_count=100`` coverage
   ``chartable_points=76`` (distinct from probability).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0304-phase-303-coverage-confidence-history-chart.md](0304-phase-303-coverage-confidence-history-chart.md)
- [0306-phase-305-distinct-as-of-assessment-history.md](0306-phase-305-distinct-as-of-assessment-history.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
