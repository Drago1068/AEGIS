# ADR-0289: Phase 288 NAS Live Verification of Phase 287 (draft)

- Status: Proposed (pending Phase 287 + live evidence)
- Date: 2026-07-31

## Context

Phase 287 would surface an unlabeled label-ready empty callout from existing
evidence-summary fields (ADR-0288). Operators need a verified frontend redeploy under
lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate frontend.
2. ``verify.ps1`` pass; evidence-summary still reports
   ``scan_unlabeled_label_ready_count`` (+ related unlabeled fields; UI unit-tested).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 287 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0288-phase-287-unlabeled-label-ready-empty-callout.md](0288-phase-287-unlabeled-label-ready-empty-callout.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
