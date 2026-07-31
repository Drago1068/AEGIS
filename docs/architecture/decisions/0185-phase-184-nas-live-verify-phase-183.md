# ADR-0185: Phase 184 NAS Live Verification of Phase 183

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``af08753``)
- Date: 2026-07-31

## Context

Phase 183 adds ``latest_calibration_corpus_count`` on evidence summary (ADR-0184). Operators
need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_calibration_corpus_count`` (null OK;
   checklist item 87).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``af08753``
(checklist item 87; AAPL ``latest_calibration_corpus_count=100``;
``latest_calibration_computed_at=2026-07-31T05:33:06.868262Z``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0184-phase-183-evidence-summary-latest-calibration-corpus-count.md](0184-phase-183-evidence-summary-latest-calibration-corpus-count.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
