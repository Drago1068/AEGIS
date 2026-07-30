# ADR-0062: Phase 61 Assessment History Filter by Component Source

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 60 live evidence showed AAPL ``mixed_component_source_assessment_count=19`` among
the newest 100 assessments. Operators need to list and export those rows (or any exact
``component_source``) without scrolling an unfiltered history. Filtering must remain
research-only and must not change assessment math or fail-closed gates.

## Decisions

### 1. Query parameter

Authenticated:

- ``GET /research/{symbol}/assessments?limit=&component_source=``
- ``GET /research/{symbol}/assessments/export?limit=&component_source=``

``component_source`` is optional:

- omitted / empty → unfiltered (current behavior)
- ``mixed`` → only assessments whose resolved component source is ``mixed``
- any other non-empty string → exact match on ``component_source_of(snapshot)``
  (``components.component_source`` if set, else ``input_source``)

Invalid empty-after-strip is treated as omitted. No new fail-closed product gates.

### 2. Scan then filter

When ``component_source`` is set, the handler loads up to ``ASSESSMENT_FILTER_SCAN_LIMIT``
(252) newest assessments, filters in domain order (newest first), then returns at most
``limit`` matches. Unfiltered requests keep loading exactly ``limit`` rows.

### 3. Console

Research console assessment history adds a source filter (All / mixed / alpha_vantage /
polygon) shared by list refresh and JSON download. History rows include ``src=…`` for
auditability.

### 4. Out of scope

- Changing assessment/label math
- Default-on calibration
- Actionable promotion, orders, ACME
- NAS live verify (follow-up ops phase)

## Related documents

- [0060-phase-59-cross-source-provenance-evidence-summary.md](0060-phase-59-cross-source-provenance-evidence-summary.md)
- [0061-phase-60-nas-live-verify-phase-59.md](0061-phase-60-nas-live-verify-phase-59.md)
- [0039-phase-38-assessment-history-export.md](0039-phase-38-assessment-history-export.md)
