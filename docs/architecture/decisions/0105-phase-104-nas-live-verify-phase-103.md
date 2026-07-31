# ADR-0105: Phase 104 NAS Live Verification of Phase 103

- Status: Accepted (pending Phase 103 + live evidence)
- Date: 2026-07-30

## Context

Phase 103 will note that calibration controls always use ``latest`` when the label panel
is on a different assessment (ADR-0104). Operators need a verified frontend redeploy on
the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Phase 103 UX accepted via unit tests; live verify does not automate browser clicks.
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 103 is on HEAD: git archive → NAS; rebuild frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0104-phase-103-calibration-controls-note-scan-labeled.md](0104-phase-103-calibration-controls-note-scan-labeled.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
