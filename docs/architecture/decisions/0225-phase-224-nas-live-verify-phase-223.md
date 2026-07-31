# ADR-0225: Phase 224 NAS Live Verification of Phase 223

- Status: Proposed (pending Phase 223 + live evidence)
- Date: 2026-07-31

## Context

Phase 223 adds ``most_recent_labeled_outcome_label_bar_source`` on evidence summary (ADR-0224).
Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after
that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``most_recent_labeled_outcome_label_bar_source``
   (null OK when no scan-labeled rows; checklist item 107).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 223 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
# Expect: OK Phase 224 most_recent_labeled_outcome_label_bar_source=… (AAPL non-null)
```

## Related documents

- [0224-phase-223-evidence-summary-most-recent-labeled-outcome-label-bar-source.md](0224-phase-223-evidence-summary-most-recent-labeled-outcome-label-bar-source.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
