# ADR-0149: Phase 148 NAS Live Verification of Phase 147

- Status: Accepted (live verified 2026-07-30; backend+frontend recreate of ``cab03a4``)
- Date: 2026-07-30

## Context

Phase 147 adds ``latest_coverage_confidence`` on evidence summary (ADR-0148). Operators
need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_coverage_confidence`` (null OK;
   checklist item 69).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-30 for ``cab03a4``
(checklist item 69; AAPL ``latest_coverage_confidence=0.75``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0148-phase-147-evidence-summary-latest-coverage-confidence.md](0148-phase-147-evidence-summary-latest-coverage-confidence.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
