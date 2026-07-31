# ADR-0209: Phase 208 NAS Live Verification of Phase 207

- Status: Proposed (pending Phase 207 + live evidence)
- Date: 2026-07-31

## Context

Phase 207 adds ``latest_outcome_label_state`` on evidence summary (ADR-0208). Operators need
a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_outcome_label_state`` (null OK;
   checklist item 99).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 207 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0208-phase-207-evidence-summary-latest-outcome-label-state.md](0208-phase-207-evidence-summary-latest-outcome-label-state.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
