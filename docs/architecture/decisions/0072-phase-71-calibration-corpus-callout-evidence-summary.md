# ADR-0072: Phase 71 Calibration Corpus Callout on Evidence Summary

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 65–69 grew mixed-assessment labeling and surfaced mixed labeled/unlabeled counts on
the evidence summary. Operators still must look at the separate readiness panel to see
``corpus_count`` / ``min_corpus`` after that labeling. Phase 70 NAS live verify remains
blocked when SSH is unavailable; this phase is console-only product work using existing
nested ``calibration_readiness`` fields (no new API contracts).

## Decisions

### 1. Console

Evidence-summary section adds:

- **Calibration corpus (readiness)** — ``corpus_count / min min_corpus``
- **Calibration bucket (readiness)** — ``bucket_count / min min_bucket``

Values come from ``evidenceSummary.calibration_readiness`` already returned by
``GET .../evidence-summary``. Research-only; no invented confidence.

### 2. Out of scope

- New API fields
- Closing Phase 70 NAS live verify (requires SSH deploy)
- Default-on calibration, gate changes
- Actionable promotion, orders, ACME

## Related documents

- [0070-phase-69-mixed-labeled-count-evidence-summary.md](0070-phase-69-mixed-labeled-count-evidence-summary.md)
- [0071-phase-70-nas-live-verify-phases-67-69.md](0071-phase-70-nas-live-verify-phases-67-69.md)
- [0017-phase-16-calibration-readiness.md](0017-phase-16-calibration-readiness.md)
