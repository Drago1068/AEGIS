# ADR-0246: Phase 245 Evidence Summary Latest Label Forward Bar Shortfall

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 241–244 completed the unlabeled tip pair (id + as_of). Live AAPL shows tip
``126`` / ``2026-07-29`` with ``scan_unlabeled_label_ready_count=0`` and
``latest_assessment_label_block_reason=insufficient_forward_bars``. Operators know *why*
labeling is blocked but not **how many forward trading sessions are still missing** before
the tip (or latest) becomes label-ready — the unlock signal for outcome-label backfill.

Further tip scalars (duplicate as_of lifts) are low value; shortfall is actionable.

## Decisions

### 1. API

Add ``latest_assessment_forward_bar_shortfall: int | null`` (+ export):

- When latest assessment exists and block reason is ``insufficient_forward_bars``, count
  how many additional trading sessions of stored bars are needed to satisfy the max
  forward horizon (``FORWARD_HORIZON_SESSIONS``, currently 20).
- ``0`` when label-ready; null when no assessment or block reason is ``no_as_of_bar``
  (shortfall not applicable). Never invent.

### 2. Console

``data-testid="evidence-latest-assessment-forward-bar-shortfall"``.

### 3. Out of scope

UI modularization, inventing ready targets, default-on calibration, orders.

### 4. Why this next

Tip id/as_of answered “which unlabeled row?” Shortfall answers “when does backfill
unlock?” — the remaining operator gap behind ``insufficient_forward_bars``.

## Resume (after Phase 244 gate)

```powershell
# Implement latest_assessment_forward_bar_shortfall (ADR-0246); tests; commit+push; then Phase 246:
# git archive HEAD → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0234-phase-233-evidence-summary-latest-assessment-label-block-reason.md](0234-phase-233-evidence-summary-latest-assessment-label-block-reason.md)
- [0244-phase-243-evidence-summary-most-recent-unlabeled-as-of.md](0244-phase-243-evidence-summary-most-recent-unlabeled-as-of.md)
- [0245-phase-244-nas-live-verify-phase-243.md](0245-phase-244-nas-live-verify-phase-243.md)
- [0247-phase-246-nas-live-verify-phase-245.md](0247-phase-246-nas-live-verify-phase-245.md)
