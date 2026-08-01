# ADR-0293: Phase 292 NAS Live Verification of Phase 291

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 291 elevated a mixed-unlabeled backlog callout inside labeling diagnostics
(ADR-0292). Operators needed a verified frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``bfe3d7c`` via ``git archive``; preserved ``.env.nas``; rebuilt
   frontend TLS compose.
2. ``verify.ps1`` passed (exit 0) against lab HTTPS with insecure + resolve.
3. Alembic ``0009`` / ``head``.

### 2. Live evidence (AAPL, 2026-08-01)

- ``mixed_unlabeled=7`` ``mixed_total=26`` ``mixed_labeled=19``
  ``label_bar_source=alpha_vantage``
- Phase 290 triggers include ``mixed_unlabeled_backlog`` (with tip/freshness/unlabeled)
- Upload ≠ verified; retain verify stdout.

## Related documents

- [0292-phase-291-mixed-unlabeled-backlog-callout.md](0292-phase-291-mixed-unlabeled-backlog-callout.md)
- [0294-phase-293-collapsible-labeling-diagnostics.md](0294-phase-293-collapsible-labeling-diagnostics.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
