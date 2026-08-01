# ADR-0293: Phase 292 NAS Live Verification of Phase 291 (draft)

- Status: Proposed (pending Phase 291 + live evidence)
- Date: 2026-07-31

## Context

Phase 291 would surface a mixed-unlabeled backlog callout from existing
evidence-summary fields inside the labeling-diagnostics group (ADR-0292). Operators need
a verified frontend redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate frontend.
2. ``verify.ps1`` pass; evidence-summary still reports
   ``mixed_unlabeled_assessment_count`` (+ related mixed fields; UI unit-tested).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 291 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0292-phase-291-mixed-unlabeled-backlog-callout.md](0292-phase-291-mixed-unlabeled-backlog-callout.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
