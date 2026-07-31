# ADR-0251: Phase 250 NAS Live Verification of Phase 249 (draft)

- Status: Proposed (pending Phase 249 + live evidence)
- Date: 2026-07-31

## Context

Phase 249 would add ``latest_assessment_last_available_label_bar_date`` (ADR-0250). Operators
need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass.
3. Evidence-summary includes ``latest_assessment_last_available_label_bar_date`` (null OK;
   checklist TBD).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 249 on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0250-phase-249-evidence-summary-latest-last-available-label-bar-date.md](0250-phase-249-evidence-summary-latest-last-available-label-bar-date.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
