# ADR-0285: Phase 284 NAS Live Verification of Phase 283 (draft)

- Status: Proposed (pending Phase 283 + live evidence)
- Date: 2026-07-31

## Context

Phase 283 would surface a latest-assessment label-readiness callout from existing
evidence-summary fields (ADR-0284). Operators need a verified frontend redeploy under
lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate frontend.
2. ``verify.ps1`` pass; evidence-summary still reports
   ``latest_assessment_is_label_ready`` / block reason / shortfall (UI unit-tested).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 283 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0284-phase-283-latest-label-readiness-callout.md](0284-phase-283-latest-label-readiness-callout.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
