# ADR-0301: Phase 300 NAS Live Verification of Phase 299 (draft)

- Status: Proposed (pending Phase 299 + live evidence)
- Date: 2026-08-01

## Context

Phase 299 would add a research-index history chart from the assessments list
(ADR-0300). Operators need a verified frontend redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate frontend.
2. ``verify.ps1`` pass; retain prior Phase 290/294/298 labeling logs; UI unit-tested chart.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 299 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0300-phase-299-research-index-history-chart.md](0300-phase-299-research-index-history-chart.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
