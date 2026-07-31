# ADR-0185: Phase 184 NAS Live Verification of Phase 183

- Status: Proposed (pending Phase 183 + live evidence)
- Date: 2026-07-31

## Context

Phase 183 adds ``latest_calibration_corpus_count`` on evidence summary (ADR-0184). Operators
need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_calibration_corpus_count`` (null OK;
   checklist item 87 after Phase 183 lands).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 183 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0184-phase-183-evidence-summary-latest-calibration-corpus-count.md](0184-phase-183-evidence-summary-latest-calibration-corpus-count.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
