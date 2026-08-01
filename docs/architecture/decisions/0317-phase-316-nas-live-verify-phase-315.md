# ADR-0317: Phase 316 NAS Live Verification of Phase 315 (draft)

- Status: Proposed (pending Phase 315 + live evidence)
- Date: 2026-08-01

## Context

Phase 315 would expose partial vs complete label coverage counts on evidence-summary
(ADR-0316). Operators need a verified NAS redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; rebuild backend + frontend.
2. ``verify.ps1`` pass; assert evidence-summary includes complete/partial labeled counts.
3. Alembic ``0009`` / ``head`` (or newer if Phase 315 migrates — expected none).

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 315 on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0316-phase-315-partial-complete-label-coverage.md](0316-phase-315-partial-complete-label-coverage.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
