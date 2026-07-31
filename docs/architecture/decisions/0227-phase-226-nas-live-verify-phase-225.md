# ADR-0227: Phase 226 NAS Live Verification of Phase 225

- Status: Proposed (pending Phase 225 + live evidence)
- Date: 2026-07-31

## Context

Phase 225 adds ``most_recent_labeled_outcome_label_computed_at`` on evidence summary
(ADR-0226). Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab
TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``most_recent_labeled_outcome_label_computed_at``
   (null OK when no scan-labeled rows; checklist item 108).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 225 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
# Expect: OK Phase 226 most_recent_labeled_outcome_label_computed_at=… (AAPL non-null)
```

## Related documents

- [0226-phase-225-evidence-summary-most-recent-labeled-outcome-label-computed-at.md](0226-phase-225-evidence-summary-most-recent-labeled-outcome-label-computed-at.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
