# ADR-0153: Phase 152 NAS Live Verification of Phase 151

- Status: Proposed (pending Phase 151 + live evidence)
- Date: 2026-07-30

## Context

Phase 151 adds ``latest_as_of_trading_date`` on evidence summary (ADR-0152). Operators need
a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_as_of_trading_date`` (null OK).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 151 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0152-phase-151-evidence-summary-latest-as-of-date.md](0152-phase-151-evidence-summary-latest-as-of-date.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
