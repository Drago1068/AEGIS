# ADR-0269: Phase 268 NAS Live Verification of Phase 267 (draft)

- Status: Proposed (pending Phase 267 + live evidence)
- Date: 2026-07-31

## Context

Phase 267 would resolve mixed label bar source in evidence-summary (ADR-0268). Operators
need a verified backend redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend.
2. ``verify.ps1`` pass; evidence-summary ``latest_resolved_label_bar_source`` is concrete
   when mixed assessment has resolvable as-of close (``mixed`` OK only when unresolved).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 267 on HEAD: git archive → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0268-phase-267-resolve-mixed-label-bar-source-evidence.md](0268-phase-267-resolve-mixed-label-bar-source-evidence.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
