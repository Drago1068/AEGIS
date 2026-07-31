# ADR-0244: Phase 243 Evidence Summary Most Recent Unlabeled As-Of (draft)

- Status: Proposed (ready after Phase 242; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 241–242 added ``most_recent_unlabeled_assessment_id``. Live AAPL shows id ``126``
(equals latest) with ``scan_unlabeled_label_ready_count=0`` and block reason
``insufficient_forward_bars``. Operators comparing the unlabeled tip to labeled and
labelable as_of dates need the **as_of_trading_date of that unlabeled tip** without
loading the assessment row. Distinct from
``most_recent_unlabeled_labelable_as_of_trading_date`` (null when tip is not ready).

## Decisions (proposed)

### 1. API

Add ``most_recent_unlabeled_as_of_trading_date: date | null`` (+ export):

- Copy ``as_of_trading_date`` from the newest scanned unlabeled assessment
  (same row as ``most_recent_unlabeled_assessment_id``).
- Null when none unlabeled. Never invent.

### 2. Console

``data-testid="evidence-most-recent-unlabeled-as-of-trading-date"``.

### 3. Out of scope

UI modularization, inventing label-ready targets, default-on calibration, orders.

### 4. Why this next

Id answered “which row?”; as_of answers “how fresh is the unlabeled tip?” — completing the
tip pair without another nested extract.

## Resume (after Phase 242 gate)

```powershell
# Implement most_recent_unlabeled_as_of_trading_date (ADR-0244); tests; commit+push; then Phase 244:
# git archive HEAD → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0242-phase-241-evidence-summary-most-recent-unlabeled-assessment-id.md](0242-phase-241-evidence-summary-most-recent-unlabeled-assessment-id.md)
- [0243-phase-242-nas-live-verify-phase-241.md](0243-phase-242-nas-live-verify-phase-241.md)
- [0245-phase-244-nas-live-verify-phase-243.md](0245-phase-244-nas-live-verify-phase-243.md)
