# ADR-0296: Phase 295 Primary Fetch Fallback Callout

- Status: Proposed (Phase 294 closed; ready to implement)
- Date: 2026-08-01

## Context

Labeling diagnostics are elevated and collapsible (Phases 283–294). Live verify still
often reports ``latest_primary_fetch_fallback=full_to_compact`` on evidence-summary
while multi-source daily-bars tip may be polygon with null fallback. Operators already
have the scalar in the grid; the panel does not elevate primary compact-fallback as a
data-quality note separate from labeling.

Prefer a fail-closed UI callout from the existing field over new tip scalars.

## Decisions

### 1. Primary fetch-fallback callout

When ``latest_primary_fetch_fallback`` is a non-empty string, show a research-only
callout (outside the labeling-diagnostics disclosure) with existing fields only:

- ``latest_primary_fetch_fallback``
- ``latest_input_source`` when present
- ``latest_as_of_trading_date`` when present

Hidden when fallback is null or empty. Never invent bars; no orders.

### 2. Out of scope

New API scalars, changing ingest policy, inventing closes, orders, calibration
default-on.

## Related documents

- [0295-phase-294-nas-live-verify-phase-293.md](0295-phase-294-nas-live-verify-phase-293.md)
- [0297-phase-296-nas-live-verify-phase-295.md](0297-phase-296-nas-live-verify-phase-295.md)
