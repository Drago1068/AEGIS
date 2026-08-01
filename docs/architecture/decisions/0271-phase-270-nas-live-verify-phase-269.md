# ADR-0271: Phase 270 NAS Live Verification of Phase 269 (draft)

- Status: Proposed (pending Phase 269 + live evidence)
- Date: 2026-07-31

## Context

Phase 269 would diagnose/fix remaining store tip calendar lag when providers already
have the current session close (ADR-0270). Operators need a verified backend redeploy
under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend.
2. ``verify.ps1`` pass; evidence tip / ``stored_bar_calendar_lag_trading_days`` reflects
   real provider closes (lag=0 when session tip is stored; lag>0 only when providers
   genuinely lack the close).
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 269 on HEAD: git archive → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0270-phase-269-advance-store-tip-current-session.md](0270-phase-269-advance-store-tip-current-session.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
