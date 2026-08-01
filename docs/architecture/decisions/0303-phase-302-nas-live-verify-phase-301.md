# ADR-0303: Phase 302 NAS Live Verification of Phase 301 (draft)

- Status: Proposed (pending Phase 301 + live evidence)
- Date: 2026-08-01

## Context

Phase 301 raises assessment history list limit to 100 for denser research-index chart
points (ADR-0302). Operators need a verified frontend redeploy under lab TLS.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate frontend.
2. ``verify.ps1`` pass; Phase 300-style chartable_points log preferably with ``limit=100``.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 301 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0302-phase-301-assessment-history-limit-100.md](0302-phase-301-assessment-history-limit-100.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
