# ADR-0019: Phase 18 On-Demand Probability Calibration

- Status: Accepted
- Date: 2026-07-29

## Context

Phase 15 added `research_calibration_v1` with optional automatic calibration after labels
(`AEGIS_RESEARCH_CALIBRATION_AFTER_LABEL_ENABLED`, default false). Phase 16 added read-only
readiness diagnostics. Operators needed an explicit path to persist a calibration when
readiness is `ready` without enabling the global automatic flag.

## Decisions

### 1. On-demand routes

Authenticated:

- `POST /research/{symbol}/assessments/{assessment_id}/calibrations` — compute and append
  one `research_calibration_v1` row using Phase 15 math and corpus gates. Fail closed with
  HTTP **422** and structured `detail.reason` / `detail.message` on gate failure; persist
  nothing.
- `GET /research/{symbol}/assessments/{assessment_id}/calibrations/latest` — newest
  calibration for that assessment, or **404**.

### 2. Method reuse

No new calibration method. Reuse `ResearchProbabilityCalibrationService.calibrate_assessment`
and the same corpus / bucket thresholds from settings.

### 3. State and confidence separation

- Calibration rows keep `state = research_only`.
- Assessment snapshot rows are not updated in place; API overlays remain as in Phase 15.
- `coverage_confidence` is never merged with `probability_confidence`.

### 4. Automatic flag unchanged

`AEGIS_RESEARCH_CALIBRATION_AFTER_LABEL_ENABLED` remains default `false`. On-demand POST does
not require that flag to be true.

### 5. Frontend

Operator console may offer “Compute calibration” when readiness status is `ready` and an
assessment id is present. Display values as calibrated research-only; no client-side math.

## Consequences

- Operators can record calibrations deliberately after readiness passes.
- Thin corpora still fail closed on POST without inventing confidence.

## Explicitly out of scope

- Default-on automatic calibration
- Multi-horizon method changes
- Actionable promotion, recommendations, orders
- NAS live deploy changes

## Related documents

- [0016-phase-15-research-probability-calibration.md](0016-phase-15-research-probability-calibration.md)
- [0017-phase-16-calibration-readiness.md](0017-phase-16-calibration-readiness.md)
- [../overview.md](../overview.md)
