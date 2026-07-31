# ADR-0184: Phase 183 Evidence Summary Latest Calibration Corpus Count

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes calibration id, horizon, and computed_at at the top level.
Operators still dig into ``latest_calibration.corpus_count`` to see how large the
calibration corpus was for that row. A top-level field keeps readiness-adjacent provenance
visible without inventing counts. Distinct from nested ``calibration_readiness`` corpus
thresholds.

## Decisions

### 1. API

Add ``latest_calibration_corpus_count: int | null`` to ``ResearchEvidenceSummaryResponse``
(+ export). Copy from ``latest_calibration.corpus_count`` when present; otherwise null.
``ge=0`` when set. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest calibration computed_at
(``data-testid="evidence-latest-calibration-corpus-count"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0182-phase-181-evidence-summary-latest-calibration-computed-at.md](0182-phase-181-evidence-summary-latest-calibration-computed-at.md)
- [0185-phase-184-nas-live-verify-phase-183.md](0185-phase-184-nas-live-verify-phase-183.md)
