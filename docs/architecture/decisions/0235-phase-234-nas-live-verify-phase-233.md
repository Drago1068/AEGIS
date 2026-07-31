# ADR-0235: Phase 234 NAS Live Verification of Phase 233

- Status: Proposed (pending NAS SSH restore + live evidence)
- Date: 2026-07-31

## Context

Phase 233 adds ``latest_assessment_label_block_reason`` on evidence summary (ADR-0234;
implemented on ``main`` at ``9dee476``). Operators need a verified backend+frontend redeploy
on the UGREEN NAS under lab TLS after that lands.

**Ops note (2026-07-31):** Host ``192.168.1.12`` responds to ICMP, but TCP/SSH port 22
refuses connections (banner exchange fails). Phase 234 cannot proceed until SSH is restored.

## Decisions

### 1. Scope

1. Deploy current ``HEAD`` with TLS overlay; recreate **backend** and **frontend**.
2. Run `verify.ps1` / `verify.sh` successfully (prior gates remain).
3. Authenticated evidence-summary includes ``latest_assessment_label_block_reason``
   (null OK when ready or no assessment; checklist item 112).
4. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New scoring math, default-on calibration, ACME, actionable promotion, orders.

## Resume

```powershell
# When NAS SSH accepts connections again:
# git archive HEAD (9dee476+) → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
# Expect: OK Phase 234 latest_assessment_label_block_reason=insufficient_forward_bars (AAPL)
```

## Related documents

- [0234-phase-233-evidence-summary-latest-assessment-label-block-reason.md](0234-phase-233-evidence-summary-latest-assessment-label-block-reason.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
