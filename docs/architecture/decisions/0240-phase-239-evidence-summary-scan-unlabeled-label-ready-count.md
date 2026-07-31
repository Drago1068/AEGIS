# ADR-0240: Phase 239 Evidence Summary Scan Unlabeled Label-Ready Count (draft)

- Status: Proposed (ready after Phase 238; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 237–238 added ``most_recent_unlabeled_labelable_as_of_trading_date``. Live AAPL shows
that field **null** while ``unlabeled_assessment_count=3`` and
``most_recent_labelable_as_of_trading_date=2026-02-05`` (already labeled). Operators infer
“no backfill work” from a null date; an explicit **count of unlabeled and label-ready** rows
in the scan makes emptiness fail-closed and auditable (and pairs with backfill
``assessment_count=0``).

## Decisions (proposed)

### 1. API

Add ``scan_unlabeled_label_ready_count: int`` (+ export):

- Count assessments in the newest-first scan that are unlabeled **and**
  ``is_snapshot_label_ready``.
- Always a non-negative integer; ``0`` when none (including empty scan). Never invent.
- Reuse bars + labeled ids from ``scan_label_diagnostics`` (extend return or compute in the
  same one-load pass).

### 2. Console

``data-testid="evidence-scan-unlabeled-label-ready-count"``.

### 3. Out of scope

UI modularization, redundant nested lifts, default-on calibration, orders, inventing
backfill targets.

### 4. Why this next

Null unlabeled+labelable as_of answers “what date?”; the count answers “how many ready
backfill candidates in scan?” — clarifying the live gap where unlabeled=3 but backfill
finds zero.

## Resume (after Phase 238 gate)

```powershell
# Implement scan_unlabeled_label_ready_count (ADR-0240); tests; commit+push; then Phase 240:
# git archive HEAD → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0238-phase-237-evidence-summary-most-recent-unlabeled-labelable-as-of.md](0238-phase-237-evidence-summary-most-recent-unlabeled-labelable-as-of.md)
- [0239-phase-238-nas-live-verify-phase-237.md](0239-phase-238-nas-live-verify-phase-237.md)
- [0241-phase-240-nas-live-verify-phase-239.md](0241-phase-240-nas-live-verify-phase-239.md)
