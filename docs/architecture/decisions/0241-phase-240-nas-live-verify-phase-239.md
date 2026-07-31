# ADR-0241: Phase 240 NAS Live Verification of Phase 239

- Status: Accepted (pending live evidence)
- Date: 2026-07-31

## Context

Phase 239 adds ``scan_unlabeled_label_ready_count`` (ADR-0240). Operators need a verified
backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy ``HEAD`` TLS; recreate backend+frontend.
2. ``verify.ps1`` / ``verify.sh`` pass.
3. Evidence-summary includes ``scan_unlabeled_label_ready_count`` (0 OK; checklist item 115).
4. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout.

## Resume

```powershell
# After Phase 239 on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0240-phase-239-evidence-summary-scan-unlabeled-label-ready-count.md](0240-phase-239-evidence-summary-scan-unlabeled-label-ready-count.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
