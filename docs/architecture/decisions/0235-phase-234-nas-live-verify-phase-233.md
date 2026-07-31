# ADR-0235: Phase 234 NAS Live Verification of Phase 233 (draft)

- Status: Proposed (pending Phase 233 + live evidence)
- Date: 2026-07-31

## Context

Phase 233 would add ``latest_assessment_label_block_reason`` on evidence summary (ADR-0234).
Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after
that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_assessment_label_block_reason``
   (null OK when ready or no assessment; checklist item TBD).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New scoring math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 233 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0234-phase-233-evidence-summary-latest-assessment-label-block-reason.md](0234-phase-233-evidence-summary-latest-assessment-label-block-reason.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
