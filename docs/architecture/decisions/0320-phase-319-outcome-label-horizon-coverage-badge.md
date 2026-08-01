# ADR-0320: Phase 319 Outcome-Label Horizon Coverage Badge (draft)

- Status: Proposed
- Date: 2026-08-01

## Context

Evidence-summary now reports scan-wide complete vs partial labeled counts and elevates a
callout when partials exist. When operators load outcome-label history for a single
assessment, each row still shows raw ``labels`` without an explicit complete/partial
coverage badge against configured horizons, so partial ready-horizons rows are easy to
misread as full labels.

## Decisions (proposed)

### 1. Per-row coverage badge (UI-only)

- On outcome-label history rows, derive coverage from existing ``labels`` keys vs
  configured horizons (``forward_return_5`` + ``forward_return_20`` / same rule as
  ``label_covers_configured_horizons``).
- Show research-only ``complete`` or ``partial`` badge plus present key list; no new API
  fields.
- Fail-closed: never invent missing horizon values.

### 2. Out of scope

Backend schema changes, auto upgrade, inventing bars, orders, changing backfill.

## Resume

```powershell
# Implement Phase 319 outcome-label horizon coverage badge; tests; commit+push; then:
# git archive HEAD → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0318-phase-317-partial-label-upgrade-callout.md](0318-phase-317-partial-label-upgrade-callout.md)
- [0319-phase-318-nas-live-verify-phase-317.md](0319-phase-318-nas-live-verify-phase-317.md)
- [0321-phase-320-nas-live-verify-phase-319.md](0321-phase-320-nas-live-verify-phase-319.md)
