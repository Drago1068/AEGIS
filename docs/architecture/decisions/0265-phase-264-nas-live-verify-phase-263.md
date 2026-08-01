# ADR-0265: Phase 264 NAS Live Verification of Phase 263 (draft)

- Status: Proposed (pending Phase 263 + live evidence)
- Date: 2026-07-31

## Context

Phase 263 would add ingest primary tip diagnostic (ADR-0264). Operators need a verified
backend redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend (frontend if changed).
2. ``verify.ps1`` pass; ingest logs primary tip beside winning tip when present.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 263 on HEAD: git archive → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0264-phase-263-ingest-primary-tip-diagnostic.md](0264-phase-263-ingest-primary-tip-diagnostic.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
