# ADR-0285: Phase 284 NAS Live Verification of Phase 283

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 283 elevated a latest-assessment label-readiness callout from existing
evidence-summary fields (ADR-0284). Operators needed a verified frontend redeploy
under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``9033ef7`` via ``git archive``; preserved ``.env.nas``; rebuilt
   frontend TLS compose.
2. ``verify.ps1`` passed (exit 0) against lab HTTPS with insecure + resolve.
3. Alembic ``0009`` / ``head``.

### 2. Live evidence (AAPL, 2026-07-31)

- ``latest_assessment_is_label_ready=False``
- ``latest_assessment_label_block_reason=insufficient_forward_bars``
- ``latest_assessment_forward_bar_shortfall=20``
- ``latest_assessment_required_label_end_date=2026-08-28``
- ``most_recent_labelable_as_of_trading_date=2026-02-05``
- ``scan_labeled_freshness_lag_trading_days=121``
- Upload ≠ verified; retain verify stdout.

## Related documents

- [0284-phase-283-latest-label-readiness-callout.md](0284-phase-283-latest-label-readiness-callout.md)
- [0286-phase-285-labeled-freshness-lag-callout.md](0286-phase-285-labeled-freshness-lag-callout.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
