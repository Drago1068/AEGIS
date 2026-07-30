# ADR-0083: Phase 82 NAS Live Verification of Phase 81

- Status: Accepted (pending live evidence)
- Date: 2026-07-30

## Context

Phase 81 added a one-click load of outcome labels for ``most_recent_labeled_assessment_id``
(ADR-0082). Operators need a verified frontend redeploy on the UGREEN NAS under lab TLS.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend** (backend optional if already
   on Phase 79/80).
2. Run `verify.ps1` / `verify.sh` successfully (prior gates including Phase 80 remain).
3. Phase 81 UX accepted via unit tests; live verify does not automate browser clicks.
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0082-phase-81-load-scan-labeled-labels.md](0082-phase-81-load-scan-labeled-labels.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
