# ADR-0236: Phase 235 Evidence Summary Most Recent Labelable As-Of Trading Date

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 229–234 completed the *latest-row* label gap diagnostics: freshness lag,
``is_label_ready``, and ``label_block_reason``. Live AAPL still shows lag≈119 with
scan-labeled as_of far behind latest. Operators need the **newest as_of that can be
labeled today** — distinct from scan-labeled (already labeled) and latest (often blocked).

## Decisions

### 1. API

Add ``most_recent_labelable_as_of_trading_date: date | null`` to evidence summary (+ export):

- Via ``OutcomeLabelService.scan_label_diagnostics``: load bars once; walk assessments
  newest-first; first ``is_snapshot_label_ready`` wins.
- Null when none are label-ready. Never invent dates.

### 2. Console

``data-testid="evidence-most-recent-labelable-as-of-trading-date"``.

### 3. Out of scope

UI modularization, redundant scalar lifts, companion assessment id (later), default-on
calibration, orders.

## Related documents

- [0235-phase-234-nas-live-verify-phase-233.md](0235-phase-234-nas-live-verify-phase-233.md)
- [0237-phase-236-nas-live-verify-phase-235.md](0237-phase-236-nas-live-verify-phase-235.md)
