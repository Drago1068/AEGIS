# ADR-0302: Phase 301 Assessment History Limit 100

- Status: Accepted (implement with Phase 300 close)
- Date: 2026-08-01

## Context

Phase 299–300 shipped a research-index history chart fed from the assessments list.
Live verify at ``limit=20`` produced only ``chartable_points=2`` after as_of dedupe
(repeated tip assessments share dates). Evidence-summary already scans ≤100 rows.
Operators need denser chart series without new API scalars.

## Decisions

### 1. History list limit

Raise the assessment panel history fetch (and matching export when used from the same
control path) from ``20`` to ``100``, aligning with the evidence-summary scan window.
Keep research-only labeling; fail-closed chart adapter unchanged. Update unit tests that
assert the list ``limit`` query.

### 2. Out of scope

New backend scalars, inventing assessments, orders, changing evidence-summary scan
semantics beyond alignment of the UI list limit.

## Related documents

- [0301-phase-300-nas-live-verify-phase-299.md](0301-phase-300-nas-live-verify-phase-299.md)
- [0303-phase-302-nas-live-verify-phase-301.md](0303-phase-302-nas-live-verify-phase-301.md)
