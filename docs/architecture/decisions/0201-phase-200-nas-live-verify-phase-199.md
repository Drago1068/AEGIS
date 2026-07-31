# ADR-0201: Phase 200 NAS Live Verification of Phase 199

- Status: Proposed (pending Phase 199 + live evidence)
- Date: 2026-07-31

## Context

Phase 199 adds ``latest_outcome_label_computed_at`` on evidence summary (ADR-0200). Operators
need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_outcome_label_computed_at`` (null OK;
   checklist item 95 after Phase 199 lands).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 199 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0200-phase-199-evidence-summary-latest-outcome-label-computed-at.md](0200-phase-199-evidence-summary-latest-outcome-label-computed-at.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
