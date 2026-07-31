# ADR-0089: Phase 88 NAS Live Verification of Phase 87

- Status: Accepted (live verified 2026-07-30; frontend recreate of ``6cf4ae8``)
- Date: 2026-07-30

## Context

Phase 87 will bind outcome-label JSON download to the loaded assessment id (ADR-0088).
Operators need a verified frontend redeploy on the UGREEN NAS under lab TLS after that
lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 87 UX accepted via unit tests; live verify does not automate browser clicks.
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 87 is on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0088-phase-87-outcome-label-download-loaded-assessment.md](0088-phase-87-outcome-label-download-loaded-assessment.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
