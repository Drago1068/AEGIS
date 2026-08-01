# ADR-0299: Phase 298 NAS Live Verification of Phase 297

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 297 appended an active-count badge on the labeling-diagnostics summary
(ADR-0298). Operators needed a verified frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``ab47a60`` via ``git archive``; preserved ``.env.nas``;
   rebuilt frontend TLS; waited ``/ready`` via docker-exec urllib.
2. ``verify.ps1`` passed. Live AAPL: ``active_count=4`` with triggers
   ``tip_not_ready,freshness_lag,unlabeled_empty,mixed_unlabeled_backlog``.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0298-phase-297-labeling-diagnostics-summary-count.md](0298-phase-297-labeling-diagnostics-summary-count.md)
- [0300-phase-299-research-index-history-chart.md](0300-phase-299-research-index-history-chart.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
