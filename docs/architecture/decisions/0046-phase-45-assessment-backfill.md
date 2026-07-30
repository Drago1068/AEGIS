# ADR-0046: Phase 45 Historical Research Assessment Backfill

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 43 can re-label existing assessments, but live NAS history is thin (often a single
recent assessment that fails labeling for insufficient forward bars). Operators need a
research-only way to create point-in-time assessments for past trading dates from stored
bars so labeling can grow the corpus toward calibration readiness—without inventing
confidence or enabling automatic calibration.

Today ``ResearchAssessmentService.assess`` always windows the latest loaded bars.
Constructor ``as_of`` only affects freshness checks and does not truncate the series.

## Decisions

### 1. Scope

Add authenticated **batch assessment backfill** for a symbol:

1. Load recent stored bars (same ``BAR_LOAD_LIMIT`` buffer as on-demand assess).
2. Build up to ``limit`` candidate ``as_of`` dates from distinct primary-quality bar dates
   (newest first).
3. Skip candidates whose ``as_of_trading_date`` already exists among recent assessment
   history (reason ``assessment_already_exists``).
4. For each remaining date: truncate bars to ``trading_date <= as_of``, call existing
   ``assess_from_bars(..., as_of=as_of)``, append on success; on
   ``ResearchAssessmentUnavailableError`` or unexpected error, skip and continue.
5. Always return **HTTP 200** with a summary (Phase 43 style). On-demand
   ``POST .../assessments`` remains the strict **422** path.

### 2. API and console

- ``POST /research/{symbol}/assessments/backfill?limit=`` (default 20, max 100).
- Operator console: "Backfill assessments" with research-only copy and count summary.
- Do **not** auto-run outcome labels or calibration during this batch (operators use Phase 43
  label backfill separately). Flags and defaults unchanged.

### 3. Evidence rules

- Append-only snapshots only; ``probability_confidence`` stays null.
- Point-in-time: bars after the candidate ``as_of`` must not enter the lookback window.
- Fail-closed skips reuse Phase 6 reason codes where applicable.

### 4. Out of scope

- Default-on / automatic calibration
- Rewriting or deleting historical rows
- Blended bars / new methods
- Guaranteeing readiness becomes ``ready``
- Actionable promotion, recommendations, orders
- ACME / public TLS

## Related documents

- [0007-phase-6-research-only-scoring.md](0007-phase-6-research-only-scoring.md)
- [0044-phase-43-outcome-label-backfill.md](0044-phase-43-outcome-label-backfill.md)
- [0045-phase-44-nas-live-verify-phase-43.md](0045-phase-44-nas-live-verify-phase-43.md)
