# ADR-0259: Phase 258 NAS Live Verification of Phase 257 (draft)

- Status: Proposed (pending Phase 257 + live evidence)
- Date: 2026-07-31

## Context

Phase 257 would exercise on-demand ingest tip refresh (ADR-0258). Operators need a
verified TLS redeploy (if code/scripts change) and live verify evidence that ingest ran
and evidence-summary lag/tip were observed.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS if Phase 257 changed runtime images; otherwise scripts-only OK.
2. ``verify.ps1`` / ``verify.sh`` pass including Phase 257 ingest checklist item.
3. Retain pre/post ``stored_bar_calendar_lag_trading_days`` (and tip dates) in stdout.
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 257 on HEAD: git archive → NAS if needed; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0258-phase-257-on-demand-ingest-tip-refresh.md](0258-phase-257-on-demand-ingest-tip-refresh.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
