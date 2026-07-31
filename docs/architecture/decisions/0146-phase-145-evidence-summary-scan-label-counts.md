# ADR-0146: Phase 145 Evidence Summary Scan-Wide Label Counts

- Status: Accepted
- Date: 2026-07-30

## Context

Evidence summary already reports mixed-source labeled/unlabeled counts and
``most_recent_labeled_*``. Operators still lack scan-wide labeled vs unlabeled totals
across the ≤100 newest assessments (not only mixed). Panel UI modularization is
complete; prefer product/evidence improvements.

## Decisions

### 1. API

Add to ``ResearchEvidenceSummaryResponse`` (and export JSON):

- ``labeled_assessment_count`` — scanned assessments (≤100) with a default-method label
- ``unlabeled_assessment_count`` — ``assessment_count - labeled_assessment_count`` (clamped ≥0)

Reuse existing ``assessment_ids_with_labels``; never invent labels.

### 2. Console

Surface both counts on ``ResearchEvidenceSummarySection`` near the assessments count.
Type them on the frontend API client. No new endpoints.

### 3. Out of scope

New calibration math, default-on calibration, orders, ACME, further UI structural extracts.

## Related documents

- [0023-phase-22-research-evidence-summary.md](0023-phase-22-research-evidence-summary.md)
- [0147-phase-146-nas-live-verify-phase-145.md](0147-phase-146-nas-live-verify-phase-145.md)
