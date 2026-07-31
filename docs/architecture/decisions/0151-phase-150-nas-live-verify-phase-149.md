# ADR-0151: Phase 150 NAS Live Verification of Phase 149

- Status: Accepted (live verified 2026-07-30; backend+frontend recreate of ``16ce17a``)
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

Retain live verify stdout as evidence. Live verify passed 2026-07-30 for ``16ce17a``
(checklist item 70; AAPL ``latest_research_index≈0.483``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0150-phase-149-evidence-summary-latest-research-index.md](0150-phase-149-evidence-summary-latest-research-index.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
