# ADR-0014: Phase 13 Research Outcome Labels (Calibration Evidence Prep)

- Status: Accepted
- Date: 2026-07-29

## Context

Phases 6–8 and 11–12 established research-only assessments, scheduled snapshots, multi-source
coverage, and corrected daily bars. `probability_confidence` remains intentionally null until a
calibration phase with evidence gates and a superseding ADR. Phase 13 adds **append-only
outcome labels** linked to assessment snapshots so a future calibration phase has labeled
examples without implying calibrated probabilities or actionable advice today.

## Decisions

### 1. Label method `forward_total_return_v1`

For a stored assessment snapshot, compute deterministic forward **total returns** from the
as-of session close using stored daily bars only:

- `forward_return_5`: close at the 5th exchange trading session **after**
  `as_of_trading_date` / close at `as_of_trading_date` − 1
- `forward_return_20`: same for 20 trading sessions after

Horizons are trading-session counts on `AEGIS_EXCHANGE_CALENDAR_NAME`, not calendar days.
Bar selection uses the snapshot's `input_source` when it is a single source id; when
`input_source` is `mixed` (Phase 11 cross-source fill), labels use the as-of close from the
same component series rules documented in the assessment `components` (`component_source`).

### 2. State and confidence

- Every label row has `state = research_only`.
- Labels are **outcomes for evidence**, not `probability_confidence` and not merged with
  `coverage_confidence`.
- Assessment snapshots keep `probability_confidence = null`.

### 3. Storage

Append-only table `research_assessment_outcome_labels`:

- `assessment_snapshot_id` FK to `research_assessment_snapshots.id`
- `label_method_id`, `label_method_version`, `schema_version`
- `labels` JSONB (numeric forward returns keyed by horizon name)
- `label_end_dates` JSONB (trading date of each horizon's end close)
- `bar_source` (provenance for the as-of / forward closes)
- Insert-only; always append on successful compute

### 4. Fail closed

If any configured horizon cannot be computed (missing as-of close, insufficient forward
sessions in stored bars), return HTTP **422** with structured `detail.reason` and **persist
nothing**. Reasons include `assessment_not_found`, `no_as_of_bar`,
`insufficient_forward_bars`.

### 5. Trigger

On-demand only: `POST /research/{symbol}/assessments/{assessment_id}/outcome-labels`.
Read: `GET .../outcome-labels/latest` (newest label for that assessment id). No scheduler
hook in Phase 13.

### 6. Auth

Same Phase 4 operator session gate as other `/research*` routes.

### 7. Frontend

Presentation-only display of label values on the symbol page when available; no client-side
label math.

## Explicitly out of scope

- Non-null `probability_confidence` / calibration fitting
- Actionable promotion, recommendations, orders
- Automatic labeling after ingest or assessment
- Portfolio or cross-symbol analytics
- Live NAS deployment

## Related documents

- [0007-phase-6-research-only-scoring.md](0007-phase-6-research-only-scoring.md)
- [0012-phase-11-multi-source-coverage-weighting.md](0012-phase-11-multi-source-coverage-weighting.md)
- [0013-phase-12-provider-historical-corrections.md](0013-phase-12-provider-historical-corrections.md)
