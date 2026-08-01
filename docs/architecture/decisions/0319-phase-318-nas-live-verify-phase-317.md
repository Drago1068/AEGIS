# ADR-0319: Phase 318 NAS Live Verification of Phase 317 (draft)

- Status: Proposed (pending Phase 317 + live evidence)
- Date: 2026-08-01

## Context

Phase 317 would add a labeling-diagnostics callout when
``partial_labeled_assessment_count > 0`` (ADR-0318). Operators need a verified NAS
redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; rebuild frontend (and backend if API changed — expected UI-only).
2. ``verify.ps1`` pass; assert evidence-summary still returns complete/partial counts;
   callout field bundle unit-tested (live may show partial=0).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 317 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0318-phase-317-partial-label-upgrade-callout.md](0318-phase-317-partial-label-upgrade-callout.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
