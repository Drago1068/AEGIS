# ADR-0017: Phase 16 Calibration Corpus Readiness & Operator Diagnostics

- Status: Accepted
- Date: 2026-07-29

## Context

Phase 15 added `research_calibration_v1` behind
`AEGIS_RESEARCH_CALIBRATION_AFTER_LABEL_ENABLED` (default false). Operators lacked a
read-only view of whether labeled corpus gates would pass before enabling calibration.
Phase 16 adds diagnostics without new calibration math, actionable promotion, or orders.

## Decisions

### 1. Read-only readiness API

Authenticated `GET /research/{symbol}/calibration-readiness` returns:

- `status`: `ready` | `no_assessment` | `missing_research_index` |
  `insufficient_labeled_corpus` | `insufficient_similar_examples`
- `assessment_snapshot_id`, `research_index` (from latest assessment when available)
- `corpus_count`, `bucket_count`
- effective thresholds: `min_corpus`, `min_bucket`, `index_bucket_width`
- `calibration_method_id` (`research_calibration_v1`)
- `detail` human-readable explanation

The endpoint **persists nothing** and never invents `probability_confidence`.

### 2. Domain reuse

`evaluate_calibration_readiness` reuses Phase 15 corpus selection and gate thresholds
(excluding the target assessment id from the historical corpus). No new label or
calibration method.

### 3. Frontend

Operator console research panel shows readiness diagnostics from the API only (status,
corpus/bucket counts, detail). Copy marks the section as diagnostics / research-only /
not advice. No client-side calibration math.

### 4. Auth

Same Phase 4 operator session gate as other `/research*` routes.

## Consequences

- Operators can inspect gate readiness before enabling Phase 15 calibration.
- Thin corpora remain fail-closed for calibration; readiness reports the reason without
  writing rows.

## Explicitly out of scope

- Changing the default of `AEGIS_RESEARCH_CALIBRATION_AFTER_LABEL_ENABLED`
- Actionable promotion, recommendations, orders
- Multi-horizon calibration changes
- NAS live deployment

## Related documents

- [0016-phase-15-research-probability-calibration.md](0016-phase-15-research-probability-calibration.md)
- [../overview.md](../overview.md)
- [../../operations/configuration.md](../../operations/configuration.md)
