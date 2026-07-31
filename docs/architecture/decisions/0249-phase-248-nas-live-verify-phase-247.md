# ADR-0249: Phase 248 NAS Live Verification of Phase 247 (draft)

- Status: Proposed (pending Phase 247 + live evidence)
- Date: 2026-07-31

## Context

Phase 247 would add ``latest_assessment_required_label_end_date`` (ADR-0248). Operators need
a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass.
3. Evidence-summary includes ``latest_assessment_required_label_end_date`` (null OK;
   checklist TBD).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 247 on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0248-phase-247-evidence-summary-latest-required-label-end-date.md](0248-phase-247-evidence-summary-latest-required-label-end-date.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
