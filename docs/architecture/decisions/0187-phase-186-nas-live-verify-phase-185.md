# ADR-0187: Phase 186 NAS Live Verification of Phase 185

- Status: Proposed (pending Phase 185 + live evidence)
- Date: 2026-07-31

## Context

Phase 185 adds ``latest_calibration_bucket_count`` on evidence summary (ADR-0186). Operators
need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_calibration_bucket_count`` (null OK;
   checklist item 88).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 185 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0186-phase-185-evidence-summary-latest-calibration-bucket-count.md](0186-phase-185-evidence-summary-latest-calibration-bucket-count.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
