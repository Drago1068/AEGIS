# ADR-0149: Phase 148 NAS Live Verification of Phase 147

- Status: Proposed (pending Phase 147 + live evidence)
- Date: 2026-07-30

## Context

Phase 147 adds top-level ``latest_coverage_confidence`` on evidence summary (ADR-0148).
Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_coverage_confidence`` (checklist item
   after Phase 146 item 68).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 147 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0148-phase-147-evidence-summary-latest-coverage-confidence.md](0148-phase-147-evidence-summary-latest-coverage-confidence.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
