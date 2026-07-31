# ADR-0155: Phase 154 NAS Live Verification of Phase 153

- Status: Proposed (pending Phase 153 + live evidence)
- Date: 2026-07-30

## Context

Phase 153 adds ``latest_bar_count`` on evidence summary (ADR-0154). Operators need a
verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_bar_count`` (null OK).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 153 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0154-phase-153-evidence-summary-latest-bar-count.md](0154-phase-153-evidence-summary-latest-bar-count.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
