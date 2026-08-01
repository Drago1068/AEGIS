# ADR-0334: Phase 333 Tip-Not-Ready Ready-Horizon CTA

- Status: Accepted
- Date: 2026-08-01

## Context

Phases 283–284 surface a tip-not-ready callout when
``latest_assessment_is_label_ready === false``. Live NAS remains calendar-blocked
(``forward_shortfall=20`` until ~2026-08-28; ``min_shortfall=5`` until ~2026-08-07).
Other labeling callouts now carry opt-in CTAs; tip-not-ready did not point at
``Compute ready-horizon labels`` for the earliest unlock path.

## Decisions

### 1. Tip-not-ready CTA (UI-only)

- When ``latest_assessment_is_label_ready === false`` (existing callout), add a
  research-only CTA line pointing at ``Compute ready-horizon labels`` (no auto-run).
- Source of truth: existing evidence-summary fields only; no new API scalars.
- Complements (does not replace) the Phase 321 min-horizon unlock CTA when
  ``min_horizon_shortfall === 0``.
- Callout CTA ``data-testid="evidence-label-readiness-callout-cta"``.

### 2. Out of scope

Auto-labeling, inventing bars, orders, changing shortfall math, changing unlock gates.

## Related documents

- [0333-phase-332-nas-live-verify-phase-331.md](0333-phase-332-nas-live-verify-phase-331.md)
- [0284-phase-283-latest-label-readiness-callout.md](0284-phase-283-latest-label-readiness-callout.md)
- [0322-phase-321-min-horizon-unlock-cta.md](0322-phase-321-min-horizon-unlock-cta.md)
- [0335-phase-334-nas-live-verify-phase-333.md](0335-phase-334-nas-live-verify-phase-333.md)
