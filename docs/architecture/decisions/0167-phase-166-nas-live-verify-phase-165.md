# ADR-0167: Phase 166 NAS Live Verification of Phase 165

- Status: Proposed (pending Phase 165 + live evidence)
- Date: 2026-07-31

## Context

Phase 165 adds ``latest_schema_version`` on evidence summary (ADR-0166). Operators need a
verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_schema_version`` (null OK).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 165 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0166-phase-165-evidence-summary-latest-schema-version.md](0166-phase-165-evidence-summary-latest-schema-version.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
