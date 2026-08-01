# ADR-0303: Phase 302 NAS Live Verification of Phase 301

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 301 raised assessment history list/export limit to 100 (ADR-0302) so the
research-index chart had denser as_of series after dedupe. Operators needed a
verified frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``0e4fb29`` via ``git archive``; preserved ``.env.nas``;
   rebuilt frontend TLS; waited ``/ready`` via docker-exec urllib.
2. ``verify.ps1`` passed. Live AAPL: ``list_count=100`` ``chartable_points=77``
   (was ``2`` at limit 20).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0302-phase-301-assessment-history-limit-100.md](0302-phase-301-assessment-history-limit-100.md)
- [0304-phase-303-coverage-confidence-history-chart.md](0304-phase-303-coverage-confidence-history-chart.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
