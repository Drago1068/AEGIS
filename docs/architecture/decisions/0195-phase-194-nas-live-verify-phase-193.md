# ADR-0195: Phase 194 NAS Live Verification of Phase 193

- Status: Proposed (pending Phase 193 + live evidence)
- Date: 2026-07-31

## Context

Phase 193 adds ``latest_calibration_state`` on evidence summary (ADR-0194). Operators need a
verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_calibration_state`` (null OK;
   checklist item 92).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 193 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0194-phase-193-evidence-summary-latest-calibration-state.md](0194-phase-193-evidence-summary-latest-calibration-state.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
