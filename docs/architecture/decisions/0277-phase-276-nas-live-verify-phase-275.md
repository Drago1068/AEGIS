# ADR-0277: Phase 276 NAS Live Verification of Phase 275 (draft)

- Status: Proposed (pending Phase 275 + live evidence)
- Date: 2026-07-31

## Context

Phase 275 would surface primary fetch fallback on ingest results (ADR-0276). Operators
need a verified backend redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend.
2. ``verify.ps1`` pass; ingest logs ``primary_fetch_fallback`` when compact fallback ran
   (null OK when full succeeded or primary unused).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 275 on HEAD: git archive → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0276-phase-275-ingest-primary-fetch-fallback.md](0276-phase-275-ingest-primary-fetch-fallback.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
