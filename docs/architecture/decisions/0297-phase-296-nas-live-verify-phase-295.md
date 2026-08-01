# ADR-0297: Phase 296 NAS Live Verification of Phase 295 (draft)

- Status: Proposed (pending Phase 295 + live evidence)
- Date: 2026-08-01

## Context

Phase 295 would surface a primary fetch-fallback data-quality callout from existing
evidence-summary fields (ADR-0296). Operators need a verified frontend redeploy under
lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate frontend.
2. ``verify.ps1`` pass; evidence-summary still reports
   ``latest_primary_fetch_fallback`` (UI unit-tested).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 295 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0296-phase-295-primary-fetch-fallback-callout.md](0296-phase-295-primary-fetch-fallback-callout.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
