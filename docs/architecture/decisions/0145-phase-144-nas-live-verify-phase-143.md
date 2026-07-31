# ADR-0145: Phase 144 NAS Live Verification of Phase 143

- Status: Accepted (pending Phase 143 + live evidence)
- Date: 2026-07-30

## Context

Phase 143 extracts the research assessment error alert (ADR-0144). Operators need a
verified frontend redeploy on the UGREEN NAS under lab TLS after that lands
(behavior-preserving).

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 143 accepted via unit tests; live verify does not automate browser clicks.
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 143 is on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0144-phase-143-extract-research-assessment-error-alert.md](0144-phase-143-extract-research-assessment-error-alert.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
