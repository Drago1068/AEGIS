# ADR-0066: Phase 65 Prefer Mixed Assessments in Outcome-Label Backfill

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 62 live evidence showed ~19 AAPL assessments with ``component_source=mixed``. Operators
can filter and one-click audit those rows (Phases 61–64), but outcome-label backfill still
consumed ``limit`` in newest-first order among unlabeled label-ready peers. True-mixed
assessments also failed source-aware readiness when ``resolve_label_bar_source`` returned
literal ``mixed`` (no observation source id), so they never entered the candidate set.

## Decisions

### 1. Candidate ordering

``select_label_backfill_candidates`` still requires unlabeled + label-ready (ADR-0050 /
ADR-0058). Among eligible candidates it now returns **mixed first** (newest-first within
the mixed tier), then non-mixed (newest-first), then applies ``limit``.

### 2. True-mixed label bar source

When ``input_source`` / ``component_source`` is truly ``mixed`` and bars are available,
``resolve_label_bar_source(snapshot, bars)`` picks a concrete source:

1. First ``components.coverage_sources`` entry with a usable as-of close
2. Else any usable as-of bar's ``source``
3. Else ``mixed`` (compute / readiness still fail closed)

Single-source and mixed-with-uniform-``component_source`` behavior is unchanged. No invented
closes.

### 3. Out of scope

- Weakening skip reasons or label gates
- Default-on calibration
- Actionable promotion, orders, ACME
- NAS live verify (follow-up ops phase)

## Related documents

- [0050-phase-49-prefer-unlabeled-label-backfill.md](0050-phase-49-prefer-unlabeled-label-backfill.md)
- [0058-phase-57-source-aware-label-backfill-throughput.md](0058-phase-57-source-aware-label-backfill-throughput.md)
- [0014-phase-13-research-outcome-labels.md](0014-phase-13-research-outcome-labels.md)
- [0062-phase-61-assessment-history-component-source-filter.md](0062-phase-61-assessment-history-component-source-filter.md)
