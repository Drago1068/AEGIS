# ADR-0243: Phase 242 NAS Live Verification of Phase 241

- Status: Accepted (pending live evidence)
- Date: 2026-07-31

## Context

Phase 241 adds ``most_recent_unlabeled_assessment_id`` (ADR-0242). Operators need a
verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass.
3. Evidence-summary includes ``most_recent_unlabeled_assessment_id`` (null OK;
   checklist item 116).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 241 on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0242-phase-241-evidence-summary-most-recent-unlabeled-assessment-id.md](0242-phase-241-evidence-summary-most-recent-unlabeled-assessment-id.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
