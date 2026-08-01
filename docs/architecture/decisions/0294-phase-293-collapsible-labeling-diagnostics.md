# ADR-0294: Phase 293 Collapsible Labeling Diagnostics

- Status: Accepted
- Date: 2026-08-01

## Context

Phases 283–292 elevated four research-only callouts inside
``evidence-labeling-diagnostics``. Live AAPL often shows all four at once, creating a
tall warn stack above the evidence-summary grid. Prefer a collapsible group (no new API
scalars) so operators can scan then collapse without losing fail-closed detail.

## Decisions

### 1. Collapsible wrapper

``evidence-labeling-diagnostics`` is a ``details`` element with ``open`` by default when
any callout is present. Summary control remains research-only. Individual callout
testids and field contents are unchanged.

### 2. Out of scope

New API scalars, inventing labels/closes, orders, removing callouts, calibration
default-on.

## Related documents

- [0293-phase-292-nas-live-verify-phase-291.md](0293-phase-292-nas-live-verify-phase-291.md)
- [0295-phase-294-nas-live-verify-phase-293.md](0295-phase-294-nas-live-verify-phase-293.md)
