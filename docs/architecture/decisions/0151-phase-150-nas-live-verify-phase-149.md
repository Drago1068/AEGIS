# ADR-0151: Phase 150 NAS Live Verification of Phase 149

- Status: Accepted (pending Phase 149 + live evidence)
- Date: 2026-07-30

## Context

Phase 149 adds ``latest_research_index`` on evidence summary (ADR-0150). Operators need a
verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_research_index`` (null OK; checklist
   item 70).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 149 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0150-phase-149-evidence-summary-latest-research-index.md](0150-phase-149-evidence-summary-latest-research-index.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
