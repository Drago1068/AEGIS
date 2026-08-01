# ADR-0337: Phase 336 NAS Live Verification of Phase 335 (draft)

- Status: Proposed (pending Phase 335 + live evidence)
- Date: 2026-08-01

## Context

Phase 335 would elevate a partial-labeled upgrade CTA pointing at ``Backfill outcome labels``
(ADR-0336). Operators need a verified NAS frontend redeploy under lab TLS.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; rebuild frontend.
2. ``verify.ps1`` pass; live ``partial`` may be 0 (CTA elevates when count>0; unit-tested).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 335 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0336-phase-335-partial-labeled-upgrade-cta.md](0336-phase-335-partial-labeled-upgrade-cta.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
