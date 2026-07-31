# ADR-0199: Phase 198 NAS Live Verification of Phase 197

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``77b8901``)
- Date: 2026-07-31

## Context

Phase 197 adds ``latest_calibration_assessment_snapshot_id`` on evidence summary (ADR-0198).
Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after
that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_calibration_assessment_snapshot_id``
   (null OK; checklist item 94).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``77b8901``
(checklist item 94; AAPL ``latest_calibration_assessment_snapshot_id=126``;
``latest_calibration_probability_confidence=0.75``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0198-phase-197-evidence-summary-latest-calibration-assessment-snapshot-id.md](0198-phase-197-evidence-summary-latest-calibration-assessment-snapshot-id.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
