# ADR-0236: Phase 235 Evidence Summary Most Recent Labelable As-Of Trading Date (draft)

- Status: Proposed (pending Phase 234 live verify)
- Date: 2026-07-31

## Context

Phases 229–234 (once 234 closes) complete the *latest-row* label gap diagnostics: freshness
lag, ``is_label_ready``, and ``label_block_reason``. Live AAPL still shows lag≈119 with
scan-labeled as_of far behind latest. Operators next need the **newest as_of that can be
labeled today** — distinct from scan-labeled (already labeled) and latest (often blocked).

That is an evidence diagnostic for backfill targeting, not another nested provenance scalar.

## Decisions (proposed)

### 1. API

Add ``most_recent_labelable_as_of_trading_date: date | null`` to evidence summary (+ export):

- Scan assessments newest-first; first where ``is_snapshot_label_ready`` is true wins.
- Null when none are label-ready. Never invent dates.
- Optional companion id field can wait for a later phase.

### 2. Console

``data-testid="evidence-most-recent-labelable-as-of-trading-date"``.

### 3. Out of scope

UI modularization, redundant scalar lifts, default-on calibration, orders.

## Resume (after Phase 234)

```powershell
# Implement most_recent_labelable_as_of_trading_date (ADR-0236); tests; commit+push; then Phase 236 NAS verify.
```

## Related documents

- [0234-phase-233-evidence-summary-latest-assessment-label-block-reason.md](0234-phase-233-evidence-summary-latest-assessment-label-block-reason.md)
- [0235-phase-234-nas-live-verify-phase-233.md](0235-phase-234-nas-live-verify-phase-233.md)
- [0237-phase-236-nas-live-verify-phase-235.md](0237-phase-236-nas-live-verify-phase-235.md)
