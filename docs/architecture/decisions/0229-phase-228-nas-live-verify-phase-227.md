# ADR-0229: Phase 228 NAS Live Verification of Phase 227

- Status: Proposed (pending Phase 227 + live evidence)
- Date: 2026-07-31

## Context

Phase 227 adds ``most_recent_labeled_outcome_label_as_of_trading_date`` on evidence summary
(ADR-0228). Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab
TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes
   ``most_recent_labeled_outcome_label_as_of_trading_date`` (null OK when no scan-labeled
   rows; checklist item 109).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 227 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
# Expect: OK Phase 228 most_recent_labeled_outcome_label_as_of_trading_date=… (AAPL non-null)
```

## Related documents

- [0228-phase-227-evidence-summary-most-recent-labeled-outcome-label-as-of-trading-date.md](0228-phase-227-evidence-summary-most-recent-labeled-outcome-label-as-of-trading-date.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
