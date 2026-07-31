# ADR-0253: Phase 252 NAS Live Verification of Phase 251 (draft)

- Status: Proposed (pending Phase 251 + live evidence)
- Date: 2026-07-31

## Context

Phase 251 would add ``latest_assessment_min_horizon_forward_bar_shortfall`` (ADR-0252).
Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after
that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass.
3. Evidence-summary includes ``latest_assessment_min_horizon_forward_bar_shortfall``
   (null/0 OK; checklist TBD).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 251 on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0252-phase-251-evidence-summary-min-horizon-forward-bar-shortfall.md](0252-phase-251-evidence-summary-min-horizon-forward-bar-shortfall.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
