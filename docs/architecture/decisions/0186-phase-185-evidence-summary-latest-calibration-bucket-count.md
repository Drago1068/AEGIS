# ADR-0186: Phase 185 Evidence Summary Latest Calibration Bucket Count

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes calibration corpus_count at the top level. Operators still dig
into ``latest_calibration.bucket_count`` for the peer count used by that calibration row. A
top-level field keeps readiness-adjacent provenance visible without inventing counts.
Distinct from nested ``calibration_readiness`` bucket thresholds.

## Decisions

### 1. API

Add ``latest_calibration_bucket_count: int | null`` to ``ResearchEvidenceSummaryResponse``
(+ export). Copy from ``latest_calibration.bucket_count`` when present; otherwise null.
``ge=0`` when set. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest calibration corpus_count
(``data-testid="evidence-latest-calibration-bucket-count"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0184-phase-183-evidence-summary-latest-calibration-corpus-count.md](0184-phase-183-evidence-summary-latest-calibration-corpus-count.md)
- [0187-phase-186-nas-live-verify-phase-185.md](0187-phase-186-nas-live-verify-phase-185.md)
