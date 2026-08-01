# ADR-0279: Phase 278 NAS Live Verification of Phase 277 (draft)

- Status: Proposed (pending Phase 277 + live evidence)
- Date: 2026-07-31

## Context

Phase 277 would surface ``primary_fetch_fallback`` on the operator IngestPanel
(ADR-0278). Operators need a verified frontend redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate frontend (backend rebuild optional if unchanged).
2. ``verify.ps1`` pass; alembic ``0009`` / ``head``.
3. Confirm ingest API still returns ``primary_fetch_fallback`` (Phase 276 log line).
   UI column is unit-tested locally; browser spot-check optional.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 277 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0278-phase-277-ingest-ui-primary-fetch-fallback.md](0278-phase-277-ingest-ui-primary-fetch-fallback.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
