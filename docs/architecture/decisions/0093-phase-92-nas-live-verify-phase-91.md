# ADR-0093: Phase 92 NAS Live Verification of Phase 91

- Status: Accepted (pending Phase 91 + live evidence)
- Date: 2026-07-30

## Context

Phase 91 will keep the outcome-label panel visible with an empty-state message when a
loaded assessment has no labels (ADR-0092). Operators need a verified frontend redeploy on
the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 91 UX accepted via unit tests; live verify does not automate browser clicks.
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 91 is on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0092-phase-91-outcome-label-empty-state-loaded-assessment.md](0092-phase-91-outcome-label-empty-state-loaded-assessment.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
