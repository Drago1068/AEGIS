# ADR-0318: Phase 317 Partial-Label Upgrade Backlog Callout (draft)

- Status: Proposed
- Date: 2026-08-01

## Context

Phase 315–316 exposed ``partial_labeled_assessment_count`` on evidence-summary. Live AAPL
currently shows ``partial=0`` in the ≤100 scan (ready-horizons partials may have scrolled
out), but when partials are present operators still need an elevated labeling-diagnostics
callout so the upgrade backlog is not missed among dense summary fields.

## Decisions (proposed)

### 1. Diagnostics callout

- When ``partial_labeled_assessment_count > 0``, surface a research-only callout inside the
  existing labeling-diagnostics group (same pattern as mixed-unlabeled / freshness lag).
- Copy states upgrade eligibility once max horizon unlocks; no auto-run.
- Keep counts as the source of truth; callout is display-only.

### 2. Out of scope

Inventing bars, auto full-horizon upgrade, changing backfill selection, orders,
expanding the ≤100 scan window.

## Resume

```powershell
# Implement Phase 317 partial-label upgrade backlog callout; tests; commit+push; then:
# git archive HEAD → NAS; rebuild frontend (+ backend if needed); then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0316-phase-315-partial-complete-label-coverage.md](0316-phase-315-partial-complete-label-coverage.md)
- [0317-phase-316-nas-live-verify-phase-315.md](0317-phase-316-nas-live-verify-phase-315.md)
- [0319-phase-318-nas-live-verify-phase-317.md](0319-phase-318-nas-live-verify-phase-317.md)
