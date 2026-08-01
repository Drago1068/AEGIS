# ADR-0338: Phase 337 Calendar Unlock Ops Checkpoint (draft)

- Status: Proposed
- Date: 2026-08-01

## Context

Labeling-diagnostics CTAs are complete (tip-not-ready, freshness lag, unlabeled-empty,
mixed backlog, partial upgrade, min/full-horizon unlock, primary fetch-fallback). Live tip
remains calendar-blocked: ``min_horizon_shortfall=5`` (``min_end≈2026-08-07``) and
``forward_shortfall=20`` (``required_end≈2026-08-28``). Further UI CTA micro-phases add
little until forward bars arrive.

## Decisions (proposed)

### 1. Ops checkpoint (no new product scalars)

After the next trading session that can reduce ``min_horizon_shortfall`` toward 0:

1. Redeploy current ``main`` if needed; run ``verify.ps1``.
2. Confirm frontier fields: ``min_horizon_shortfall``, ``min_horizon_required_label_end_date``,
   ``forward_bar_shortfall``, ``latest_assessment_is_label_ready``.
3. Exercise opt-in ``Compute ready-horizon labels`` / backfill only when shortfall allows
   (fail-closed; no invented bars).
4. Record live stdout; accept when min-horizon unlock CTA path is live-evidenced
   (``min_shortfall=0``) or document remaining calendar wait.

### 2. Out of scope

New API fields, auto-labeling, inventing bars, orders, weakening fail-closed gates.

## Resume

```powershell
# After calendar progress (min_end ~2026-08-07+): git archive HEAD → NAS if needed;
# rebuild frontend TLS if UI changed; then:
.\docker\nas\scripts\verify.ps1
# Confirm Phase 322/334 CTA paths against live shortfall fields.
```

## Related documents

- [0337-phase-336-nas-live-verify-phase-335.md](0337-phase-336-nas-live-verify-phase-335.md)
- [0322-phase-321-min-horizon-unlock-cta.md](0322-phase-321-min-horizon-unlock-cta.md)
- [0334-phase-333-tip-not-ready-cta.md](0334-phase-333-tip-not-ready-cta.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
