# ADR-0323: Phase 322 NAS Live Verification of Phase 321 (draft)

- Status: Proposed (pending Phase 321 + live evidence)
- Date: 2026-08-01

## Context

Phase 321 would elevate a ready-horizons CTA when min-horizon shortfall reaches zero while
tip remains not fully label-ready (ADR-0322). Operators need a verified NAS frontend
redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; rebuild frontend.
2. ``verify.ps1`` pass; UI unit-tested CTA (live may still show shortfall>0 until
   ~2026-08-07).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 321 on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0322-phase-321-min-horizon-unlock-cta.md](0322-phase-321-min-horizon-unlock-cta.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
