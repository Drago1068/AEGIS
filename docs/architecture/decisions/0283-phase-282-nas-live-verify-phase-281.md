# ADR-0283: Phase 282 NAS Live Verification of Phase 281 (draft)

- Status: Proposed (pending Phase 281 + live evidence)
- Date: 2026-07-31

## Context

Phase 281 would surface ``fetch_fallback`` on daily-bars responses (ADR-0282).
Operators need a verified backend redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend (frontend if UI changed).
2. ``verify.ps1`` pass; optionally log tip bar ``fetch_fallback`` when present
   (``full_to_compact`` expected on AV compact tip; null OK otherwise).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 281 on HEAD: git archive → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0282-phase-281-daily-bars-fetch-fallback.md](0282-phase-281-daily-bars-fetch-fallback.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
