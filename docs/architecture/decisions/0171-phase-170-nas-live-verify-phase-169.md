# ADR-0171: Phase 170 NAS Live Verification of Phase 169

- Status: Proposed (pending Phase 169 + live evidence)
- Date: 2026-07-31

## Context

Phase 169 adds ``latest_event_time`` on evidence summary (ADR-0170). Operators need a
verified backend+frontend redeploy on the UGREEN NAS under lab TLS after that lands.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_event_time`` (null OK).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# After Phase 169 is on HEAD: git archive → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0170-phase-169-evidence-summary-latest-event-time.md](0170-phase-169-evidence-summary-latest-event-time.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
