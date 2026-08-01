# ADR-0298: Phase 297 Labeling Diagnostics Summary Count

- Status: Proposed (Phase 296 closed; ready to implement)
- Date: 2026-08-01

## Context

Phases 283–294 elevated four labeling callouts inside a collapsible disclosure. Live
AAPL often shows all four. The summary control does not yet show how many diagnostics
are active, so operators must expand to know severity at a glance.

Prefer a summary count derived from existing callout conditions (no new API scalars).

## Decisions

### 1. Summary count

On the labeling-diagnostics ``summary`` control, append a research-only count of active
callouts (1–4) derived from the same booleans that render tip-not-ready, freshness lag,
unlabeled-empty, and mixed-unlabeled backlog. Keep open-by-default; keep existing
callout testids.

### 2. Out of scope

New API scalars, inventing labels/closes, orders, removing callouts, calibration
default-on.

## Related documents

- [0297-phase-296-nas-live-verify-phase-295.md](0297-phase-296-nas-live-verify-phase-295.md)
- [0299-phase-298-nas-live-verify-phase-297.md](0299-phase-298-nas-live-verify-phase-297.md)
