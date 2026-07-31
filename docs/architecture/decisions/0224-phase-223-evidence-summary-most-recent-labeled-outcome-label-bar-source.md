# ADR-0224: Phase 223 Evidence Summary Most Recent Labeled Outcome Label Bar Source

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes scan-labeled ``most_recent_labeled_outcome_label_state``.
Operators still dig into ``most_recent_labeled_outcome_label.bar_source`` when the absolute
latest assessment is unlabeled. A top-level field keeps that bar source visible without
inventing values. Distinct from ``latest_outcome_label_bar_source`` and assessment input/source
fields.

## Decisions

### 1. API

Add ``most_recent_labeled_outcome_label_bar_source: str | null`` to
``ResearchEvidenceSummaryResponse`` (+ export). Copy from
``most_recent_labeled_outcome_label.bar_source`` when present; otherwise null. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near most recent labeled state
(``data-testid="evidence-most-recent-labeled-outcome-label-bar-source"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0222-phase-221-evidence-summary-most-recent-labeled-outcome-label-state.md](0222-phase-221-evidence-summary-most-recent-labeled-outcome-label-state.md)
- [0225-phase-224-nas-live-verify-phase-223.md](0225-phase-224-nas-live-verify-phase-223.md)
- [0226-phase-225-evidence-summary-most-recent-labeled-outcome-label-computed-at.md](0226-phase-225-evidence-summary-most-recent-labeled-outcome-label-computed-at.md)
