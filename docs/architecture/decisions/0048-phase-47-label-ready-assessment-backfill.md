# ADR-0048: Phase 47 Label-Ready Assessment Backfill Candidates

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 45 assessment backfill selected primary bar dates newest-first. Live Phase 46 verify
persisted 19 assessments near the bar tip, then Phase 43 label backfill skipped all rows
with ``insufficient_forward_bars`` (labels need closes 5 and 20 sessions after ``as_of``).
Operators need backfill to prefer as-of dates that already have stored forward horizon ends.

## Decisions

### 1. Candidate filter

``candidate_as_of_dates`` only returns primary-quality dates where the loaded bar series
contains a close on the trading session ``max(FORWARD_HORIZON_SESSIONS)`` (currently 20)
after ``as_of``, using the same calendar session advance as Phase 13 labeling.

- Order remains newest-first among **eligible** dates (not among all tip dates).
- Dates without forward coverage are omitted from the candidate list (not per-row skip
  noise). When none qualify, the backfill summary has ``candidate_count=0``.

### 2. Scope

- Domain + tests + docs only (API/console contracts unchanged).
- No change to on-demand ``POST .../assessments``, labeling math, or calibration defaults.

### 3. Out of scope

- Guaranteeing readiness becomes ``ready``
- Auto-running label backfill after assessment backfill
- Raising ``BAR_LOAD_LIMIT`` (120 remains; operators may need deeper ingest for more
  label-ready history)
- Default-on calibration, actionable promotion, orders, ACME

## Related documents

- [0046-phase-45-assessment-backfill.md](0046-phase-45-assessment-backfill.md)
- [0044-phase-43-outcome-label-backfill.md](0044-phase-43-outcome-label-backfill.md)
- [0014-phase-13-research-outcome-labels.md](0014-phase-13-research-outcome-labels.md)
