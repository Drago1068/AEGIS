# ADR-0063: Phase 62 NAS Live Verification of Phase 61

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 61 added optional ``component_source`` filtering on assessment list/export and the
operator console history (ADR-0062). Phase 60 live evidence showed ~19 mixed-source
assessments for AAPL. Operators need a verified redeploy on the UGREEN NAS under the lab
TLS profile so mixed-only list/export is live and auditable.

## Decisions

### 1. Scope

Phase 62 is an **ops evidence gate** on the HTTPS lab profile:

1. Deploy current revision with the TLS overlay (native `linux/arm64` acceptable).
2. Recreate backend (and frontend for console filter) so Phase 61 contracts are live.
3. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
4. Additionally confirm authenticated:
   - ``GET .../assessments?limit=&component_source=mixed`` → **200** JSON array
   - ``GET .../assessments/export?limit=&component_source=mixed`` → **200** attachment, JSON array
   - When evidence-summary ``mixed_component_source_assessment_count > 0``, prefer filtered
     list count ``>= 1`` (empty filtered results only OK when mixed count is 0)
   - Filtered rows must resolve to ``component_source`` / ``input_source`` ``mixed``
5. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- New assessment/label math
- Default-on calibration
- ACME / public DNS
- Actionable promotion, recommendations, orders

## Related documents

- [0062-phase-61-assessment-history-component-source-filter.md](0062-phase-61-assessment-history-component-source-filter.md)
- [0061-phase-60-nas-live-verify-phase-59.md](0061-phase-60-nas-live-verify-phase-59.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
