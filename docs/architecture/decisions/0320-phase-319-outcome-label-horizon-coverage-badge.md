# ADR-0320: Phase 319 Outcome-Label Horizon Coverage Badge

- Status: Accepted
- Date: 2026-08-01

## Context

Evidence-summary reports scan-wide complete vs partial labeled counts. When operators load
outcome-label history for a single assessment, each row still showed raw ``labels`` without
an explicit complete/partial coverage badge against configured horizons.

## Decisions

### 1. Per-row coverage badge (UI-only)

- Derive coverage from existing ``labels`` keys vs configured horizons
  (``forward_return_5`` + ``forward_return_20``; same rule as
  ``label_covers_configured_horizons``).
- Show research-only ``complete`` / ``partial`` badge plus present/missing keys; no new API
  fields.
- Fail-closed: never invent missing horizon values.

### 2. Out of scope

Backend schema changes, auto upgrade, inventing bars, orders, changing backfill.

## Related documents

- [0318-phase-317-partial-label-upgrade-callout.md](0318-phase-317-partial-label-upgrade-callout.md)
- [0319-phase-318-nas-live-verify-phase-317.md](0319-phase-318-nas-live-verify-phase-317.md)
- [0321-phase-320-nas-live-verify-phase-319.md](0321-phase-320-nas-live-verify-phase-319.md)
- [0322-phase-321-min-horizon-unlock-cta.md](0322-phase-321-min-horizon-unlock-cta.md)
