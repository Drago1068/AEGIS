# ADR-0322: Phase 321 Min-Horizon Unlock Ready-Horizons CTA

- Status: Accepted
- Date: 2026-08-01

## Context

Live AAPL tip remains blocked on max horizon while min horizon unlocks sooner. Operators
already have ready-horizons actions, but when ``min_horizon_shortfall`` hits ``0`` while tip
is still not fully label-ready, nothing elevated tip eligibility for ready-horizons compute.

## Decisions

### 1. Frontier-driven CTA (UI-only)

- When ``latest_assessment_min_horizon_forward_bar_shortfall === 0`` and
  ``latest_assessment_is_label_ready === false``, elevate a research-only labeling-diagnostics
  callout pointing at existing ``Compute ready-horizon labels`` (no auto-run).
- Source of truth remains existing frontier fields; no new API scalars.

### 2. Out of scope

Auto-labeling, inventing bars, orders, full-horizon auto-upgrade, expanding scan window.

## Related documents

- [0321-phase-320-nas-live-verify-phase-319.md](0321-phase-320-nas-live-verify-phase-319.md)
- [0310-phase-309-min-horizon-label-path.md](0310-phase-309-min-horizon-label-path.md)
- [0323-phase-322-nas-live-verify-phase-321.md](0323-phase-322-nas-live-verify-phase-321.md)
