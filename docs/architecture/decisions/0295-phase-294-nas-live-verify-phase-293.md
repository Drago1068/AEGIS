# ADR-0295: Phase 294 NAS Live Verification of Phase 293

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 293 made labeling diagnostics a collapsible disclosure open by default
(ADR-0294). Operators needed a verified frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``b8e72bc`` via ``git archive``; preserved ``.env.nas``; rebuilt
   frontend TLS compose.
2. ``verify.ps1`` passed (exit 0) against lab HTTPS with insecure + resolve.
3. Alembic ``0009`` / ``head``.

### 2. Live evidence (AAPL, 2026-08-01)

- Phase 294 disclosure open-by-default with triggers
  ``tip_not_ready,freshness_lag,unlabeled_empty,mixed_unlabeled_backlog``
- Tip still blocked until required end ``2026-08-28`` (forward-bar shortfall ``20``)
- ``latest_primary_fetch_fallback=full_to_compact`` still appears on evidence-summary
  (null after some ingest paths)
- Upload ≠ verified; retain verify stdout.

## Related documents

- [0294-phase-293-collapsible-labeling-diagnostics.md](0294-phase-293-collapsible-labeling-diagnostics.md)
- [0296-phase-295-primary-fetch-fallback-callout.md](0296-phase-295-primary-fetch-fallback-callout.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
