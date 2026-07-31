# ADR-0127: Phase 126 NAS Live Verification of Phase 125

- Status: Accepted (pending Phase 125 + live evidence)
- Date: 2026-07-30

## Context

Phase 125 groups research assessment action toolbar controls (ADR-0126). Operators need a
verified frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 125 UX accepted via unit tests; live verify does not automate browser clicks.
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 125 is on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0126-phase-125-group-research-assessment-action-toolbar.md](0126-phase-125-group-research-assessment-action-toolbar.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
