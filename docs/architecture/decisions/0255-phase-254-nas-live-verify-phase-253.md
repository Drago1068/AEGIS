# ADR-0255: Phase 254 NAS Live Verification of Phase 253 (draft)

- Status: Proposed (pending Phase 253 + live evidence)
- Date: 2026-07-31

## Context

Phase 253 would add ``latest_assessment_min_horizon_required_label_end_date`` (ADR-0254).
Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after
that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass.
3. Evidence-summary includes ``latest_assessment_min_horizon_required_label_end_date``
   (null OK; checklist item 122).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 253 on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0254-phase-253-evidence-summary-min-horizon-required-label-end-date.md](0254-phase-253-evidence-summary-min-horizon-required-label-end-date.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
