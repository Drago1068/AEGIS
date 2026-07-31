# ADR-0219: Phase 218 NAS Live Verification of Phase 217

- Status: Proposed (pending Phase 217 + live evidence)
- Date: 2026-07-31

## Context

Phase 217 adds ``most_recent_labeled_outcome_label_method_version`` on evidence summary
(ADR-0218). Operators need a verified backend+frontend redeploy on the UGREEN NAS under lab
TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``most_recent_labeled_outcome_label_method_version``
   (null OK when no scan-labeled rows; checklist item 104).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 217 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0218-phase-217-evidence-summary-most-recent-labeled-outcome-label-method-version.md](0218-phase-217-evidence-summary-most-recent-labeled-outcome-label-method-version.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
