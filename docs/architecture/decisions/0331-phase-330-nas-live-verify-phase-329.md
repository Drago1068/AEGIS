# ADR-0331: Phase 330 NAS Live Verification of Phase 329 (draft)

- Status: Proposed (pending Phase 329 + live evidence)
- Date: 2026-08-01

## Context

Phase 329 would elevate a primary fetch-fallback CTA pointing at ``Run ingest``
(ADR-0330). Operators need a verified NAS frontend redeploy under lab TLS.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; rebuild frontend.
2. ``verify.ps1`` pass; live non-empty ``latest_primary_fetch_fallback`` expected to
   elevate CTA when present (unit-tested; null OK).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 329 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0330-phase-329-primary-fetch-fallback-cta.md](0330-phase-329-primary-fetch-fallback-cta.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
