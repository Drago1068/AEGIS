# ADR-0295: Phase 294 NAS Live Verification of Phase 293 (draft)

- Status: Proposed (pending Phase 293 + live evidence)
- Date: 2026-08-01

## Context

Phase 293 would make the labeling-diagnostics group collapsible (ADR-0294). Operators
need a verified frontend redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate frontend.
2. ``verify.ps1`` pass; Phase 284/286/288/290/292 field bundles still log; UI unit-tested
   disclosure.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 293 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0294-phase-293-collapsible-labeling-diagnostics.md](0294-phase-293-collapsible-labeling-diagnostics.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
