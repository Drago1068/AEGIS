# ADR-0081: Phase 80 NAS Live Verification of Phase 79

- Status: Accepted (pending live evidence)
- Date: 2026-07-30

## Context

Phase 79 added ``most_recent_labeled_assessment_id`` and
``most_recent_labeled_outcome_label`` to evidence-summary (ADR-0080). Operators need a
verified backend+frontend redeploy on the UGREEN NAS under the lab TLS profile.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``most_recent_labeled_assessment_id`` and
   ``most_recent_labeled_outcome_label`` (null OK when no labeled rows in scan).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD to NAS aegis-src (backend+frontend TLS), then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0080-phase-79-most-recent-labeled-evidence-summary.md](0080-phase-79-most-recent-labeled-evidence-summary.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
