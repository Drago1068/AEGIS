# ADR-0245: Phase 244 NAS Live Verification of Phase 243

- Status: Accepted (pending live evidence)
- Date: 2026-07-31

## Context

Phase 243 adds ``most_recent_unlabeled_as_of_trading_date`` (ADR-0244). Operators need
a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass.
3. Evidence-summary includes ``most_recent_unlabeled_as_of_trading_date`` (null OK;
   checklist item 117).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 243 on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0244-phase-243-evidence-summary-most-recent-unlabeled-as-of.md](0244-phase-243-evidence-summary-most-recent-unlabeled-as-of.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
