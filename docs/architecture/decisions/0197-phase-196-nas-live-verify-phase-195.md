# ADR-0197: Phase 196 NAS Live Verification of Phase 195

- Status: Proposed (pending Phase 195 + live evidence)
- Date: 2026-07-31

## Context

Phase 195 adds ``latest_calibration_probability_confidence`` on evidence summary (ADR-0196).
Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after
that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_calibration_probability_confidence``
   (null OK; checklist item 93 after Phase 195 lands).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 195 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0196-phase-195-evidence-summary-latest-calibration-probability-confidence.md](0196-phase-195-evidence-summary-latest-calibration-probability-confidence.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
