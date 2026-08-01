# ADR-0328: Phase 327 Freshness-Lag Backfill CTA (draft)

- Status: Proposed
- Date: 2026-08-01

## Context

Phases 285–286 surface a labeled-corpus freshness-lag callout when
``scan_labeled_freshness_lag_trading_days > 0``. Live NAS shows ``lag=121``, but the
callout does not point operators at existing opt-in ready-horizon / outcome-label
backfill toolbar actions. Tip max-horizon labeling remains calendar-blocked until
~2026-08-28; freshness lag is actionable for catching up ready horizons without
inventing bars.

## Decisions (proposed)

### 1. Freshness-lag CTA (UI-only)

- When ``scan_labeled_freshness_lag_trading_days > 0`` (existing callout), add a
  research-only CTA line pointing at ``Backfill ready-horizon labels`` (no auto-run).
- Source of truth: existing evidence-summary fields only; no new API scalars.

### 2. Out of scope

Auto-backfill, inventing bars, orders, changing lag computation, changing unlock CTAs.

## Resume

```powershell
# Implement ADR-0328; tests; commit+push; then:
# git archive HEAD → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0327-phase-326-nas-live-verify-phase-325.md](0327-phase-326-nas-live-verify-phase-325.md)
- [0286-phase-285-labeled-freshness-lag-callout.md](0286-phase-285-labeled-freshness-lag-callout.md)
- [0329-phase-328-nas-live-verify-phase-327.md](0329-phase-328-nas-live-verify-phase-327.md)
