# ADR-0016: Phase 15 Research Probability Calibration v1

- Status: Accepted
- Date: 2026-07-29

## Context

Phases 13–14 added append-only outcome labels and automatic labeling after successful
assessments. Assessment rows still store `probability_confidence = null` at insert time.
Phase 15 introduces the first **research-only** calibrated probability using stored labeled
historical corpus evidence, without actionable promotion, recommendations, or orders.

## Decisions

### 1. Method `research_calibration_v1`

For a target assessment snapshot, compute a bounded empirical probability from labeled
historical examples for the same symbol:

1. Load labeled pairs `(research_index, forward_return_5)` from stored assessments and Phase
   13 `forward_total_return_v1` labels (newest label per assessment).
2. Exclude the target assessment id from the corpus.
3. Fail closed if historical labeled count `< AEGIS_RESEARCH_CALIBRATION_MIN_CORPUS`
   (default 10).
4. Select the similarity bucket where `|research_index - target| <=
   AEGIS_RESEARCH_CALIBRATION_INDEX_BUCKET_WIDTH` (default 0.15).
5. Fail closed if bucket count `< AEGIS_RESEARCH_CALIBRATION_MIN_BUCKET` (default 5).
6. `probability_confidence = clip(count(forward_return_5 > 0) / bucket_count, 0, 1)`.

This is an empirical hit rate, not a fitted model. It remains research-only evidence.

### 2. Storage

Append-only table `research_assessment_probability_calibrations`:

- FK to `research_assessment_snapshots.id`
- `calibration_method_id`, `calibration_method_version`, `schema_version`
- `probability_confidence`, `corpus_count`, `bucket_count`
- `state = research_only`

Assessment snapshot rows are not updated in place. API responses overlay the latest
calibration row onto `probability_confidence` for presentation.

### 3. Confidence separation

- `coverage_confidence` unchanged on assessments (Phase 6/11).
- `probability_confidence` from calibration rows only; never merged into coverage.
- Labels are inputs to calibration, not outputs merged into assessment components.

### 4. Fail closed

Insufficient corpus, insufficient bucket, missing `research_index`, or missing assessment:
structured log + **persist nothing** on automatic paths. On-demand assessment responses still
return 200 when calibration skips.

Reason codes: `insufficient_labeled_corpus`, `insufficient_similar_examples`,
`missing_research_index`, `assessment_not_found`.

### 5. Trigger and flag

`AEGIS_RESEARCH_CALIBRATION_AFTER_LABEL_ENABLED` (default **false**):

- after successful on-demand `POST /research/{symbol}/assessments` (and after optional
  labeling in the same handler);
- after successful post-ingest labeling inside the scheduled ingest lock (when research and
  labeling paths are enabled); or
- after successful post-ingest assessments when labeling is disabled but calibration is enabled.

When false, API responses keep `probability_confidence = null` unless historical calibration
rows exist from prior runs.

### 6. Auth and UI

Same operator session gate as `/research*`. Frontend shows non-null values as
**calibrated research-only** with fixed precision; no client-side calibration math.

## Consequences

- Operators can enable calibrated research-only probabilities once labeled history satisfies
  gates.
- Thin corpora remain fail-closed with null confidence in API responses.
- Actionable promotion and orders remain out of scope.

## Explicitly out of scope

- Actionable promotion, recommendations, orders
- Portfolio analytics
- NAS live deployment
- Replacing or blending `coverage_confidence`

## Related documents

- [0014-phase-13-research-outcome-labels.md](0014-phase-13-research-outcome-labels.md)
- [0015-phase-14-scheduled-outcome-labels.md](0015-phase-14-scheduled-outcome-labels.md)
- [../overview.md](../overview.md)
- [../../operations/configuration.md](../../operations/configuration.md)
