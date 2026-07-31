# ADR-0187: Phase 186 NAS Live Verification of Phase 185

- Status: Accepted (live verified 2026-07-31; backend+frontend recreate of ``8ee7b8f``)
- Date: 2026-07-31

## Context

Phase 185 adds ``latest_calibration_bucket_count`` on evidence summary (ADR-0186). Operators
need a verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_calibration_bucket_count`` (null OK;
   checklist item 88).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence. Live verify passed 2026-07-31 for ``8ee7b8f``
(checklist item 88; AAPL ``latest_calibration_bucket_count=20``;
``latest_calibration_corpus_count=100``).

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# Deploy HEAD backend+frontend to NAS under TLS, then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0186-phase-185-evidence-summary-latest-calibration-bucket-count.md](0186-phase-185-evidence-summary-latest-calibration-bucket-count.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
