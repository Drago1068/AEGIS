# ADR-0322: Phase 321 Min-Horizon Unlock Ready-Horizons CTA (draft)

- Status: Proposed
- Date: 2026-08-01

## Context

Live AAPL tip remains blocked on max horizon (``forward_bar_shortfall=20``,
``required_end=2026-08-28``) while min horizon unlocks sooner
(``min_horizon_shortfall=5``, ``min_horizon_end=2026-08-07``). Operators already have
ready-horizons actions, but when ``min_horizon_shortfall`` hits ``0`` while tip is still
not fully label-ready, nothing elevates that the tip is now eligible for
ready-horizons compute.

## Decisions (proposed)

### 1. Frontier-driven CTA (UI-only)

- When ``latest_assessment_min_horizon_forward_bar_shortfall === 0`` and
  ``latest_assessment_is_label_ready === false``, elevate a research-only callout / CTA
  hint pointing at existing ``Compute ready-horizon labels`` (no auto-run).
- Source of truth remains existing frontier fields; no new API scalars.

### 2. Out of scope

Auto-labeling, inventing bars, orders, full-horizon auto-upgrade, expanding scan window.

## Resume

```powershell
# Implement Phase 321 min-horizon unlock CTA; tests; commit+push; then:
# git archive HEAD → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0321-phase-320-nas-live-verify-phase-319.md](0321-phase-320-nas-live-verify-phase-319.md)
- [0310-phase-309-min-horizon-label-path.md](0310-phase-309-min-horizon-label-path.md)
- [0323-phase-322-nas-live-verify-phase-321.md](0323-phase-322-nas-live-verify-phase-321.md)
