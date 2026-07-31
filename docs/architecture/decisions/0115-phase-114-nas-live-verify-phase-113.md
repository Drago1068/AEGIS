# ADR-0115: Phase 114 NAS Live Verification of Phase 113

- Status: Accepted (pending Phase 113 + live evidence)
- Date: 2026-07-30

## Context

Phase 113 adds load-kind suffixes to outcome-label action accessible names (ADR-0114).
Operators need a verified frontend redeploy on the UGREEN NAS under lab TLS after that
lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 113 UX accepted via unit tests; live verify does not automate browser clicks.
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 113 is on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0114-phase-113-outcome-label-action-aria-load-kind.md](0114-phase-113-outcome-label-action-aria-load-kind.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
