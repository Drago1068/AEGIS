# ADR-0287: Phase 286 NAS Live Verification of Phase 285

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 285 elevated a labeled-corpus freshness-lag callout from existing
evidence-summary fields (ADR-0286). Operators needed a verified frontend redeploy
under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``0f7d3c6`` via ``git archive``; preserved ``.env.nas``; rebuilt
   frontend TLS compose.
2. ``verify.ps1`` passed (exit 0) against lab HTTPS with insecure + resolve.
3. Alembic ``0009`` / ``head``.

### 2. Live evidence (AAPL, 2026-07-31)

- ``scan_labeled_freshness_lag_trading_days=121``
- ``most_recent_labeled_outcome_label_as_of_trading_date=2026-02-05``
- ``latest_as_of_trading_date=2026-07-31``
- Tip still ``label_ready=False`` / ``insufficient_forward_bars`` / shortfall ``20``
- ``scan_unlabeled_label_ready_count=0`` (next product gap candidate)
- Upload ≠ verified; retain verify stdout.

## Related documents

- [0286-phase-285-labeled-freshness-lag-callout.md](0286-phase-285-labeled-freshness-lag-callout.md)
- [0288-phase-287-unlabeled-label-ready-empty-callout.md](0288-phase-287-unlabeled-label-ready-empty-callout.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
