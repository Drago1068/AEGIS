# ADR-0263: Phase 262 NAS Live Verification of Phase 261 (draft)

- Status: Proposed (pending Phase 261 + live evidence)
- Date: 2026-07-31

## Context

Phase 261 would reconcile provider tip ahead of store tip (ADR-0262). Operators need a
verified backend redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend (frontend if changed).
2. ``verify.ps1`` pass; ingest + evidence-summary show tip behavior consistent with the fix
   (provider tip / store tip / lag logged; never invent).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 261 on HEAD: git archive → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0262-phase-261-provider-tip-ahead-of-store.md](0262-phase-261-provider-tip-ahead-of-store.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
