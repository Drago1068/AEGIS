# ADR-0175: Phase 174 NAS Live Verification of Phase 173

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``64fce25``)
- Date: 2026-07-31

## Context

Phase 173 adds ``latest_assessment_id`` on evidence summary (ADR-0174). Operators need a
verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_assessment_id`` (null OK;
   checklist item 82).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``64fce25``
(checklist item 82; AAPL ``latest_assessment_id=126``,
``most_recent_labeled_assessment_id=125``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0174-phase-173-evidence-summary-latest-assessment-id.md](0174-phase-173-evidence-summary-latest-assessment-id.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
