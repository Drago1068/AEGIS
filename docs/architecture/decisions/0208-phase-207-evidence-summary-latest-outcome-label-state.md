# ADR-0208: Phase 207 Evidence Summary Latest Outcome Label State

- Status: Accepted
- Date: 2026-07-31

## Context

Evidence summary now exposes ``latest_outcome_label_schema_version``. Operators still dig into
``latest_outcome_label.state`` to confirm the label remains research-only when the latest
assessment is labeled. A top-level field keeps that identity visible without inventing
strings. Distinct from top-level summary ``state`` and ``latest_calibration_state``.

## Decisions

### 1. API

Add ``latest_outcome_label_state: str | null`` to ``ResearchEvidenceSummaryResponse``
(+ export). Copy from ``latest_outcome_label.state`` when present; otherwise null. Never
invent.

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near latest outcome label schema_version
(``data-testid="evidence-latest-outcome-label-state"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0206-phase-205-evidence-summary-latest-outcome-label-schema-version.md](0206-phase-205-evidence-summary-latest-outcome-label-schema-version.md)
- [0209-phase-208-nas-live-verify-phase-207.md](0209-phase-208-nas-live-verify-phase-207.md)
