# ADR-0173: Phase 172 NAS Live Verification of Phase 171

- Status: Proposed (pending Phase 171 + live evidence)
- Date: 2026-07-31

## Context

Phase 171 adds ``latest_probability_confidence`` on evidence summary (ADR-0172). Operators
need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_probability_confidence`` (null OK).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 171 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0172-phase-171-evidence-summary-latest-probability-confidence.md](0172-phase-171-evidence-summary-latest-probability-confidence.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
