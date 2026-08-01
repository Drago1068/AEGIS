# ADR-0281: Phase 280 NAS Live Verification of Phase 279 (draft)

- Status: Proposed (pending Phase 279 + live evidence)
- Date: 2026-07-31

## Context

Phase 279 would surface latest primary fetch fallback on evidence-summary (ADR-0280).
Operators need a verified backend redeploy under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend.
2. ``verify.ps1`` pass; log evidence-summary ``latest_primary_fetch_fallback`` when present
   (``full_to_compact`` expected when latest AV tip bar used compact; null OK otherwise).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 279 on HEAD: git archive → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0280-phase-279-evidence-summary-primary-fetch-fallback.md](0280-phase-279-evidence-summary-primary-fetch-fallback.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
