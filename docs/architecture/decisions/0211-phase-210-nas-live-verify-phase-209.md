# ADR-0211: Phase 210 NAS Live Verification of Phase 209

- Status: Proposed (pending Phase 209 + live evidence)
- Date: 2026-07-31

## Context

Phase 209 adds ``latest_outcome_label_bar_source`` on evidence summary (ADR-0210). Operators
need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_outcome_label_bar_source`` (null OK;
   checklist item 100).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 209 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0210-phase-209-evidence-summary-latest-outcome-label-bar-source.md](0210-phase-209-evidence-summary-latest-outcome-label-bar-source.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
