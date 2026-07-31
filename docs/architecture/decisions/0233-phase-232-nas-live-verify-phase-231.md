# ADR-0233: Phase 232 NAS Live Verification of Phase 231 (draft)

- Status: Proposed (pending Phase 231 + live evidence)
- Date: 2026-07-31

## Context

Phase 231 would add ``latest_assessment_is_label_ready`` on evidence summary (ADR-0232).
Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after
that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_assessment_is_label_ready``
   (null OK when no latest assessment; checklist item TBD).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New scoring math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 231 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0232-phase-231-evidence-summary-latest-assessment-is-label-ready.md](0232-phase-231-evidence-summary-latest-assessment-is-label-ready.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
