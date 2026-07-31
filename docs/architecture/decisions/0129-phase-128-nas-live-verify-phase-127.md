# ADR-0129: Phase 128 NAS Live Verification of Phase 127

- Status: Accepted (pending Phase 127 + live evidence)
- Date: 2026-07-30

## Context

Phase 127 extracts the outcome-label history panel section (ADR-0128). Operators need a
verified frontend redeploy on the UGREEN NAS under lab TLS after that lands
(behavior-preserving).

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 127 accepted via unit tests; live verify does not automate browser clicks.
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 127 is on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0128-phase-127-extract-outcome-label-history-section.md](0128-phase-127-extract-outcome-label-history-section.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
