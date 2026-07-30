# ADR-0061: Phase 60 NAS Live Verification of Phase 59

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 59 added evidence-summary provenance fields
(``latest_component_source``, ``latest_resolved_label_bar_source``,
``mixed_component_source_assessment_count``) and console display (ADR-0060). Operators need
a verified redeploy on the UGREEN NAS under the lab TLS profile.

## Decisions

### 1. Scope

Phase 60 is an **ops evidence gate** on the HTTPS lab profile:

1. Deploy current revision with the TLS overlay (native `linux/arm64` acceptable).
2. Recreate backend (and frontend for console provenance) so Phase 59 contracts are live.
3. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
4. Additionally confirm authenticated ``GET .../evidence-summary`` (and export) include:
   - ``latest_component_source`` (string or null)
   - ``latest_resolved_label_bar_source`` (string or null)
   - ``mixed_component_source_assessment_count`` (integer ≥ 0)
5. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- New assessment/label math
- Default-on calibration
- ACME / public DNS
- Actionable promotion, recommendations, orders

## Related documents

- [0060-phase-59-cross-source-provenance-evidence-summary.md](0060-phase-59-cross-source-provenance-evidence-summary.md)
- [0059-phase-58-nas-live-verify-phase-57.md](0059-phase-58-nas-live-verify-phase-57.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
