# ADR-0210: Phase 209 Evidence Summary Latest Outcome Label Bar Source

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary already exposes ``latest_resolved_label_bar_source`` (may resolve even when
the absolute newest assessment is unlabeled). Operators still want the persisted
``latest_outcome_label.bar_source`` as a top-level field that is null whenever the latest
assessment has no label row — never inventing a resolved fallback into that slot.

## Decisions

### 1. API

Add ``latest_outcome_label_bar_source: str | null`` to ``ResearchEvidenceSummaryResponse``
(+ export). Copy from ``latest_outcome_label.bar_source`` when present; otherwise null.
Distinct from ``latest_resolved_label_bar_source`` and ``latest_mixed_label_bar_source``.
Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest outcome label state
(``data-testid="evidence-latest-outcome-label-bar-source"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0208-phase-207-evidence-summary-latest-outcome-label-state.md](0208-phase-207-evidence-summary-latest-outcome-label-state.md)
- [0211-phase-210-nas-live-verify-phase-209.md](0211-phase-210-nas-live-verify-phase-209.md)
