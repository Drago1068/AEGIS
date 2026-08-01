# ADR-0273: Phase 272 NAS Live Verification of Phase 271 (draft)

- Status: Proposed (pending Phase 271 + live evidence)
- Date: 2026-07-31

## Context

Phase 271 would fix verify logging so calendar lag ``0`` is not shown as ``null``
(ADR-0272). Operators need a live TLS verify pass with correct lag display after tip
catch-up.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` (verify scripts; backend rebuild only if archive requires).
2. ``verify.ps1`` pass; post-ingest ``post_lag=0`` when tip is current.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 271 on HEAD: git archive → NAS if needed; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0272-phase-271-fix-verify-lag-zero-as-null.md](0272-phase-271-fix-verify-lag-zero-as-null.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
