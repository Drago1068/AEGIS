# ADR-0305: Phase 304 NAS Live Verification of Phase 303 (draft)

- Status: Proposed (pending Phase 303 + live evidence)
- Date: 2026-08-01

## Context

Phase 303 would add a coverage-confidence history chart from the assessments list
(ADR-0304). Operators need a verified frontend redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate frontend.
2. ``verify.ps1`` pass; retain Phase 300/302 chartable_points logs; UI unit-tested chart.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 303 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0304-phase-303-coverage-confidence-history-chart.md](0304-phase-303-coverage-confidence-history-chart.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
