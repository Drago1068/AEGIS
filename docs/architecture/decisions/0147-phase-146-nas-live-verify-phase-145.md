# ADR-0147: Phase 146 NAS Live Verification of Phase 145

- Status: Accepted (pending Phase 145 + live evidence)
- Date: 2026-07-30

## Context

Phase 145 adds scan-wide labeled/unlabeled assessment counts on evidence summary
(ADR-0146). Operators need a verified backend+frontend redeploy on the UGREEN NAS under
lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``labeled_assessment_count`` and
   ``unlabeled_assessment_count`` (checklist item 68 after renumber / append).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 145 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0146-phase-145-evidence-summary-scan-label-counts.md](0146-phase-145-evidence-summary-scan-label-counts.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
