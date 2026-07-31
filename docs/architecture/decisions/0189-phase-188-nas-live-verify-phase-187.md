# ADR-0189: Phase 188 NAS Live Verification of Phase 187

- Status: Proposed (pending Phase 187 + live evidence)
- Date: 2026-07-31

## Context

Phase 187 adds ``latest_calibration_method_id`` on evidence summary (ADR-0188). Operators
need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_calibration_method_id`` (null OK;
   checklist item 89 after Phase 187 lands).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 187 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0188-phase-187-evidence-summary-latest-calibration-method-id.md](0188-phase-187-evidence-summary-latest-calibration-method-id.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
