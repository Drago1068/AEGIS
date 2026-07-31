# ADR-0232: Phase 231 Evidence Summary Latest Assessment Is Label Ready (draft)

- Status: Proposed (ready after Phase 230; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 229–230 closed the scan-labeled freshness lag diagnostic. Live NAS evidence for AAPL
shows ``latest_outcome_label_id=null``, ``scan_labeled_freshness_lag_trading_days=119``, and
a non-null scan-labeled row. Operators can see *how stale* labels are, but not *why the
absolute latest assessment is unlabeled* — typically ``insufficient_forward_bars`` vs already
labeled vs other fail-closed reasons.

Existing domain helper ``is_snapshot_label_ready`` (and label skip reasons) already encode
this. Surfacing a top-level boolean (and optionally a compact reason) is an **evidence
diagnostic**, not another nested provenance scalar lift.

## Decisions (proposed)

### 1. API

Add ``latest_assessment_is_label_ready: bool | null`` to ``ResearchEvidenceSummaryResponse``
(+ export):

- When a latest assessment exists, evaluate label-readiness with the same calendar/horizons
  and stored forward closes used by outcome-label backfill (reuse
  ``is_snapshot_label_ready`` / related helpers; never invent closes).
- Null when no latest assessment.
- Optional follow-on (same or later phase): ``latest_assessment_label_block_reason`` string
  enum when not ready; keep Phase 231 to the boolean if reason wiring is heavy.

### 2. Console

Surface near freshness lag
(``data-testid="evidence-latest-assessment-is-label-ready"``).

### 3. Explicitly out of scope

- Nested UI modularization extracts
- Redundant copies of already-lifted scalar provenance fields
- Default-on calibration, actionable promotion, orders, new scoring math

### 4. Why this next

Lag answers "how far behind." Label-ready answers "can we close the gap on the latest row
today?" That is the remaining operator question from live AAPL evidence.

## Resume (after Phase 230 gate)

```powershell
# Implement latest_assessment_is_label_ready (ADR-0232); tests; commit+push; then Phase 232:
# git archive HEAD → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
# Expect: OK Phase 232 latest_assessment_is_label_ready=… (AAPL false when latest unlabeled for forward bars)
```

## Related documents

- [0230-phase-229-evidence-summary-scan-labeled-freshness-lag.md](0230-phase-229-evidence-summary-scan-labeled-freshness-lag.md)
- [0231-phase-230-nas-live-verify-phase-229.md](0231-phase-230-nas-live-verify-phase-229.md)
- [0233-phase-232-nas-live-verify-phase-231.md](0233-phase-232-nas-live-verify-phase-231.md)
