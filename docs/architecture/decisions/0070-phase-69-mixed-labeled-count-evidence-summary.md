# ADR-0070: Phase 69 Explicit Mixed Labeled Count on Evidence Summary

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 67 added ``mixed_unlabeled_assessment_count`` and ``latest_mixed_label_bar_source``.
Operators still derive labeled coverage as mixed − unlabeled. An explicit labeled count and
console “X of Y mixed” display make post-backfill audit clearer (Phase 66 labeled 19 mixed
rows in one pass). Phase 68 NAS live verify of Phase 67 remains blocked when SSH to the NAS
is unavailable; this phase is product-only and does not close that ops gate.

## Decisions

### 1. Evidence-summary field

``GET /research/{symbol}/evidence-summary`` (and export) add:

- ``mixed_labeled_assessment_count`` — among newest ≤100 mixed assessments, count with a
  default-method outcome label

Invariant (fail closed in composition):  
``mixed_labeled + mixed_unlabeled == mixed_component_source_assessment_count``  
(with unlabeled clamped so it never exceeds mixed count).

### 2. Console

Evidence-summary shows “Mixed labeled (scanned)” as ``N of M mixed`` beside the unlabeled
row.

### 3. Out of scope

- Closing Phase 68 NAS live verify (requires SSH deploy)
- Gate/math changes, default-on calibration
- Actionable promotion, orders, ACME

## Related documents

- [0068-phase-67-mixed-label-coverage-evidence-summary.md](0068-phase-67-mixed-label-coverage-evidence-summary.md)
- [0069-phase-68-nas-live-verify-phase-67.md](0069-phase-68-nas-live-verify-phase-67.md)
