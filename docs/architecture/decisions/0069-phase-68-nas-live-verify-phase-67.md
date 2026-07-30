# ADR-0069: Phase 68 NAS Live Verification of Phase 67

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 67 added evidence-summary fields ``mixed_unlabeled_assessment_count`` and
``latest_mixed_label_bar_source`` (ADR-0068). Operators need a verified redeploy on the
UGREEN NAS under the lab TLS profile.

## Decisions

### 1. Scope

Phase 68 is an **ops evidence gate** on the HTTPS lab profile:

1. Deploy current revision with the TLS overlay (native `linux/arm64` acceptable).
2. Recreate backend (and frontend for console rows) so Phase 67 contracts are live.
3. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
4. Additionally confirm authenticated ``GET .../evidence-summary`` (and export) include:
   - ``mixed_unlabeled_assessment_count`` (integer ≥ 0)
   - ``latest_mixed_label_bar_source`` (string or null)
5. When ``mixed_component_source_assessment_count > 0`` after Phase 66 labeling, prefer
   ``mixed_unlabeled_assessment_count`` ≤ mixed count and
   ``latest_mixed_label_bar_source`` non-null when unlabeled is strictly less than mixed
   count (zeros/null OK when no mixed rows or none labeled yet).
6. SSH `alembic current` includes **`0009`** or `head`.

### 2. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 3. Out of scope

- New assessment/label math
- Default-on calibration
- ACME / public DNS
- Actionable promotion, recommendations, orders

## Related documents

- [0068-phase-67-mixed-label-coverage-evidence-summary.md](0068-phase-67-mixed-label-coverage-evidence-summary.md)
- [0067-phase-66-nas-live-verify-phase-65.md](0067-phase-66-nas-live-verify-phase-65.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
