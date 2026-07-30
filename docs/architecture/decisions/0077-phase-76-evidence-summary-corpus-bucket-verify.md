# ADR-0077: Phase 76 Evidence-Summary Nested Corpus/Bucket Verify Assertion

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 71 surfaces aggregate ``corpus_count`` / ``min_corpus`` and bucket counts from nested
``calibration_readiness`` on the evidence summary (ADR-0072). Phase 75 locked nested
``by_horizon`` keys in live verify (ADR-0076). The aggregate corpus/bucket fields used by
the Phase 71 console callout are not yet asserted on evidence-summary (+ export).

## Decisions

### 1. Scope

Phase 76 is an **ops hardening** gate (no product math):

1. Authenticated ``GET .../evidence-summary`` requires nested
   ``calibration_readiness.corpus_count``, ``min_corpus``, ``bucket_count``, and
   ``min_bucket`` (counts ``>= 0``; mins ``>= 1``).
2. Authenticated ``GET .../evidence-summary/export`` requires the same nested fields.
3. Update `verify.ps1` / `verify.sh` checklist; prior ADR checks remain mandatory.
4. Sync verify scripts to the NAS and run live verify successfully.
5. Calibration defaults remain off; no new API fields.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

### 3. Out of scope

New readiness math, default-on calibration, ACME, actionable promotion, orders.

## Related documents

- [0072-phase-71-calibration-corpus-callout-evidence-summary.md](0072-phase-71-calibration-corpus-callout-evidence-summary.md)
- [0076-phase-75-evidence-summary-by-horizon-verify.md](0076-phase-75-evidence-summary-by-horizon-verify.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
