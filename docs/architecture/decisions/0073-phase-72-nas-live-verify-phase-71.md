# ADR-0073: Phase 72 NAS Live Verification of Phase 71 (and pending 67–70)

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 71 added evidence-summary console rows for calibration corpus/bucket from nested
readiness (ADR-0072). Phase 70 (live verify of Phases 67–69) remains blocked when NAS SSH
port 22 is down. Phase 72 is the ops gate to redeploy frontend (and backend if not yet on
``f298cf0``+) once SSH recovers.

## Decisions

### 1. Scope

When SSH is available:

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend** (and backend if Phase 67–69
   fields are not yet live).
2. Run `verify.ps1` / `verify.sh` successfully — Phase 70 checklist items remain mandatory.
3. Phase 71 UX is accepted via unit tests; live verify does not automate browser clicks.
4. SSH `alembic current` includes **`0009`** or `head`.

Successful Phase 72 live evidence after deploying current HEAD also closes Phase 70.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume when SSH recovers

```powershell
# Confirm SSH, deploy HEAD to NAS aegis-src, recreate backend+frontend under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0072-phase-71-calibration-corpus-callout-evidence-summary.md](0072-phase-71-calibration-corpus-callout-evidence-summary.md)
- [0071-phase-70-nas-live-verify-phases-67-69.md](0071-phase-70-nas-live-verify-phases-67-69.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
