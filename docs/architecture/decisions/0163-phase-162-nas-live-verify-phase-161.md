# ADR-0163: Phase 162 NAS Live Verification of Phase 161

- Status: Proposed (pending Phase 161 + live evidence)
- Date: 2026-07-31

## Context

Phase 161 adds ``latest_lookback_end_date`` on evidence summary (ADR-0162). Operators need
a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_lookback_end_date`` (null OK).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 161 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0162-phase-161-evidence-summary-latest-lookback-end.md](0162-phase-161-evidence-summary-latest-lookback-end.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
