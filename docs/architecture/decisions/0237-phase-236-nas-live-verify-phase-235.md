# ADR-0237: Phase 236 NAS Live Verification of Phase 235

- Status: Proposed (pending Phase 235 + live evidence)
- Date: 2026-07-31

## Context

Phase 235 adds ``most_recent_labelable_as_of_trading_date`` (ADR-0236). Operators need a
verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass (prior gates remain).
3. Evidence-summary includes ``most_recent_labelable_as_of_trading_date`` (null OK; checklist
   item 113).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 235 on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
# Expect: OK Phase 236 most_recent_labelable_as_of_trading_date=… (AAPL non-null when any label-ready)
```

## Related documents

- [0236-phase-235-evidence-summary-most-recent-labelable-as-of-trading-date.md](0236-phase-235-evidence-summary-most-recent-labelable-as-of-trading-date.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
