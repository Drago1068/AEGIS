# ADR-0226: Phase 225 Evidence Summary Most Recent Labeled Outcome Label Computed At

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes scan-labeled ``most_recent_labeled_outcome_label_bar_source``.
Operators still dig into ``most_recent_labeled_outcome_label.computed_at`` when the absolute
latest assessment is unlabeled. A top-level field keeps that timestamp visible without
inventing values. Distinct from ``latest_outcome_label_computed_at`` and assessment/calibration
computed_at fields.

## Decisions

### 1. API

Add ``most_recent_labeled_outcome_label_computed_at: datetime | null`` (ISO-8601 string in JSON)
to ``ResearchEvidenceSummaryResponse`` (+ export). Copy from
``most_recent_labeled_outcome_label.computed_at`` when present; otherwise null. Never invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near most recent labeled bar_source
(``data-testid="evidence-most-recent-labeled-outcome-label-computed-at"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0224-phase-223-evidence-summary-most-recent-labeled-outcome-label-bar-source.md](0224-phase-223-evidence-summary-most-recent-labeled-outcome-label-bar-source.md)
- [0227-phase-226-nas-live-verify-phase-225.md](0227-phase-226-nas-live-verify-phase-225.md)
- [0228-phase-227-evidence-summary-most-recent-labeled-outcome-label-as-of-trading-date.md](0228-phase-227-evidence-summary-most-recent-labeled-outcome-label-as-of-trading-date.md)
