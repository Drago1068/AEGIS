# ADR-0330: Phase 329 Primary Fetch-Fallback Ingest CTA

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 296 surfaces a primary fetch-fallback callout when
``latest_primary_fetch_fallback`` is non-empty (live NAS often shows ``full_to_compact``).
The callout did not point operators at the existing on-demand ingest control
(``Run ingest`` on the operator console). Tip labeling remains calendar-blocked;
ingest/fallback diagnostics are still actionable without inventing bars.

## Decisions

### 1. Primary fetch-fallback CTA (UI-only)

- When ``latest_primary_fetch_fallback`` is a non-empty string (existing callout), add a
  research-only CTA line pointing at ``Run ingest`` (no auto-run).
- Source of truth: existing evidence-summary fields only; no new API scalars.
- Callout CTA ``data-testid="evidence-primary-fetch-fallback-callout-cta"`` with
  ``use_console=Run ingest``.

### 2. Out of scope

Auto-ingest, inventing bars, orders, changing fallback detection, changing labeling CTAs.

## Related documents

- [0329-phase-328-nas-live-verify-phase-327.md](0329-phase-328-nas-live-verify-phase-327.md)
- [0296-phase-295-primary-fetch-fallback-callout.md](0296-phase-295-primary-fetch-fallback-callout.md)
- [0331-phase-330-nas-live-verify-phase-329.md](0331-phase-330-nas-live-verify-phase-329.md)
- [0332-phase-331-unlabeled-empty-cta.md](0332-phase-331-unlabeled-empty-cta.md)
