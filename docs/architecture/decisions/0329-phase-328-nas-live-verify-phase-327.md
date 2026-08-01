# ADR-0329: Phase 328 NAS Live Verification of Phase 327 (draft)

- Status: Proposed (pending Phase 327 + live evidence)
- Date: 2026-08-01

## Context

Phase 327 would elevate a freshness-lag CTA pointing at existing ready-horizon backfill
toolbar actions (ADR-0328). Operators need a verified NAS frontend redeploy under lab TLS.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; rebuild frontend.
2. ``verify.ps1`` pass; live ``freshness_lag>0`` expected to elevate CTA (unit-tested).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 327 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0328-phase-327-freshness-lag-cta.md](0328-phase-327-freshness-lag-cta.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
